#include "streamer/streamer.hpp"

#include <libuvc/libuvc.h>
#include <unistd.h>

#include <fstream>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <chrono>
#include <ctime>
#include <string>


#define VENDOR_ID 0x1e4e
#define PRODUCT_ID 0x0100

uvc_context_t * ctx;
uvc_device_t * dev;
uvc_device_handle_t * devh;
uvc_stream_ctrl_t ctrl;

streamer::Streamer streamer_;

uint16_t limit_max_temp = 31315;        // 上限温度を40度(ケルビン値100倍
uint16_t limit_min_temp = 29315;        // 下減温度を20度
uint16_t kelvin_absolute_zero = 27315;  // 絶対零度

auto last_time = std::chrono::system_clock::now();

// void process_frame(const cv::Mat &in, cv::Mat &out)
// {
//     in.copyTo(out);
// }

void stream_frame(const cv::Mat &image)
{
    streamer_.stream_frame(image.data);
}

void cb(uvc_frame_t * frame, void * ptr)
{
  cv::Mat image(frame->height, frame->width, CV_8U, cv::Scalar::all(255));

  double center_temp =
    ((double)((uint16_t *)frame->data)[frame->data_bytes / 4 + frame->width / 2] -
     kelvin_absolute_zero) /
    100.0;
  double max_temp = 0;
  double min_temp = 100000;
  int max_index = 0;
  int min_index = 0;

  for (int y = 0; y < image.rows; y++) {
    for (int x = 0; x < image.cols; x++) {
      uint16_t temp = 0;
      void * _temp = &((uchar *)frame->data)[y * frame->width * 2 + x * 2];
      temp = *((uint16_t *)_temp);
      if (temp > max_temp) {
        max_temp = temp;
        max_index = y * frame->width + x;
      }
      if (temp < min_temp) {
        min_temp = temp;
        min_index = y * frame->width + x;
      }
      if (temp < limit_min_temp) temp = limit_min_temp;
      if (temp > limit_max_temp) temp = limit_max_temp;
      temp =
        (uint8_t)(((float)(temp - limit_min_temp) / (float)(limit_max_temp - limit_min_temp)) * 255.0f);
      image.data[y * image.cols + x] = (unsigned char)temp;
    }
  }

  std::ofstream ofs("temp_info.txt");
  ofs << center_temp << "\n";
  ofs << (max_temp - kelvin_absolute_zero) / 100 << "\n";
  ofs << (min_temp - kelvin_absolute_zero) / 100 << "\n";
  ofs.close();

  //   std::cout << "center_temp: " << center_temp << "\n";
  //   std::cout << "max_temp: " << (max_temp - kelvin_absolute_zero) / 100 << "\n";
  //   std::cout << "min_temp: " << (min_temp - kelvin_absolute_zero) / 100 << "\n";

  cv::Mat color;
  cv::applyColorMap(image, color, cv::COLORMAP_JET);
  cv::circle(color, cv::Point(min_index % frame->width, min_index / frame->width), 4, cv::Scalar(255, 0, 0), 1);
  cv::circle(color, cv::Point(max_index % frame->width, max_index / frame->width), 4, cv::Scalar(0, 0, 255), 1);
  stream_frame(color);

  // cv::Mat resizeImage;
  // cv::resize(color, resizeImage, cv::Size(640, 480), cv::INTER_CUBIC);
  // cv::imshow("image", resizeImage);

  auto now = std::chrono::system_clock::now();
  auto diff = now - last_time;

  // 以下デバッグ用　cb間隔計測
  // last_time = now;
  // std::cout << std::chrono::duration_cast<std::chrono::milliseconds>(diff).count() << std::endl;

  if(diff > std::chrono::milliseconds(60000)){
    last_time = now;
    time_t current_date = time(0);
    tm *ltm = localtime(&current_date);
    std::string date_str = std::to_string(1900 + ltm->tm_year) + std::to_string(1 + ltm->tm_mon) + std::to_string(ltm->tm_mday) + std::to_string(ltm->tm_hour) + std::to_string(ltm->tm_min)  + std::to_string(ltm->tm_sec);
    cv::imwrite("./data/" + date_str + ".jpg", color);
  }

  cv::waitKey(1);  // 1msec待つ
}

int main()
{
  uvc_error_t res;

  res = uvc_init(&ctx, NULL);
  if (res < 0) {
    uvc_perror(res, "uvc_init");
    return -1;
  }

  res = uvc_find_device(ctx, &dev, VENDOR_ID, PRODUCT_ID, NULL);
  if (res < 0) {
    uvc_perror(res, "uvc_find_device");
    return -1;
  }

  res = uvc_open(dev, &devh);
  if (res < 0) {
    uvc_perror(res, "uvc_open");
    uvc_unref_device(dev);
    dev = NULL;
    return -1;
  }

  int bitrate = 500000;

  streamer::StreamerConfig streamer_config(80, 60, 80, 60, 13, bitrate, "main", "rtmp://localhost/live/test");

  streamer_.enable_av_debug_log();
  streamer_.init(streamer_config);

  res = uvc_get_stream_ctrl_format_size(devh, &ctrl, UVC_FRAME_FORMAT_GRAY16, 80, 60, 9);
  //   uvc_print_stream_ctrl(&ctrl, stderr);

  res = uvc_start_streaming(devh, &ctrl, cb, (void *)0, 0);
  if (res < 0) {
    uvc_perror(res, "start_streaming");
    uvc_stop_streaming(devh);
  }
  while (devh != NULL && dev != NULL && ctx != NULL) {
    sleep(1);
  }

  // 後処理
  if (devh != NULL) {
    uvc_stop_streaming(devh);
    uvc_close(devh);
  }
  if (dev != NULL) {
    uvc_unref_device(dev);
  }
  if (ctx != NULL) {
    uvc_exit(ctx);
    puts("UVC exited");
  }

  return 0;
}
