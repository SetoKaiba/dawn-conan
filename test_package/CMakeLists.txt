cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(dawn CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example dawn::dawn)
