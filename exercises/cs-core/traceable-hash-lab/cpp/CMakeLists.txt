cmake_minimum_required(VERSION 3.20)
project(traceable_hash_lab LANGUAGES CXX)

include(CTest)

add_library(traceable_hash_lab_lib src/hashing.cpp)
target_include_directories(traceable_hash_lab_lib PUBLIC include)
target_compile_features(traceable_hash_lab_lib PUBLIC cxx_std_20)

add_executable(traceable_hash_lab src/main.cpp)
target_link_libraries(traceable_hash_lab PRIVATE traceable_hash_lab_lib)

add_executable(traceable_hash_lab_tests tests/test_hashing.cpp)
target_link_libraries(traceable_hash_lab_tests PRIVATE traceable_hash_lab_lib)

if(MSVC)
  target_compile_options(traceable_hash_lab_lib PRIVATE /W4 /permissive-)
  target_compile_options(traceable_hash_lab PRIVATE /W4 /permissive-)
  target_compile_options(traceable_hash_lab_tests PRIVATE /W4 /permissive-)
else()
  target_compile_options(traceable_hash_lab_lib PRIVATE -Wall -Wextra -Wpedantic -Werror)
  target_compile_options(traceable_hash_lab PRIVATE -Wall -Wextra -Wpedantic -Werror)
  target_compile_options(traceable_hash_lab_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

add_test(NAME traceable_hash_lab_tests COMMAND traceable_hash_lab_tests)
