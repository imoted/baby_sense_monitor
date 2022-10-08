cmake_minimum_required(VERSION 2.8.3) ##CMake 2.8.3以上を条件として設定．
project(lepton)
set(SOURCE_FILE main.cpp)
set ( CMAKE_EXE_LINKER_FLAGS_RELEASE  "${CMAKE_EXE_LINKER_FLAGS_RELEASE} ")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -std=c++11 -Wall ")
set ( CMAKE_EXE_LINKER_FLAGS_DEBUG  "${CMAKE_EXE_LINKER_FLAGS_DEBUG} -fsanitize=address -fsanitize=undefined ")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}  -std=c++11 -Wall -O0 -fno-omit-frame-pointer -fsanitize=address -fsanitize=undefined -D__FORTIFY_SOURCE=2 -rdynamic -DDEBUG")


find_package(OpenCV REQUIRED)
find_package(libuvc REQUIRED)

find_library(AVCODEC_LIBRARY avcodec)
find_library(AVFORMAT_LIBRARY avformat)
find_library(AVUTIL_LIBRARY avutil)
find_library(SWSCALE_LIBRARY swscale)

MESSAGE(${AVFORMAT_LIBRARY})

##OpenCV関係のインクルードディレクトリのパスを設定
include_directories(
    ${OpenCV_INCLUDE_DIRS}
)

add_subdirectory(streamer)

##実行ファイル名を設定
add_executable(
    ${PROJECT_NAME} ${SOURCE_FILE}
)

##リンクするライブラリを読み込む
target_link_libraries(
    ${PROJECT_NAME} streamer ${OpenCV_LIBRARIES} ${libuvc_LIBRARIES} ${AVCODEC_LIBRARY} ${AVFORMAT_LIBRARY} ${AVUTIL_LIBRARY} ${SWSCALE_LIBRARY}
)
