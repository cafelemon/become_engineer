cmake_minimum_required(VERSION 3.20)
project(traceable_search_sort_lab LANGUAGES CXX)

include(CTest)

add_library(traceable_search_sort_lab_lib src/lab.cpp)
target_include_directories(traceable_search_sort_lab_lib PUBLIC include)
target_compile_features(traceable_search_sort_lab_lib PUBLIC cxx_std_20)

add_executable(traceable_search_sort_lab src/main.cpp)
target_link_libraries(traceable_search_sort_lab PRIVATE traceable_search_sort_lab_lib)

add_executable(traceable_search_sort_lab_tests tests/test_lab.cpp)
target_link_libraries(traceable_search_sort_lab_tests PRIVATE traceable_search_sort_lab_lib)

if(MSVC)
  target_compile_options(traceable_search_sort_lab_lib PRIVATE /W4 /permissive-)
  target_compile_options(traceable_search_sort_lab PRIVATE /W4 /permissive-)
  target_compile_options(traceable_search_sort_lab_tests PRIVATE /W4 /permissive-)
else()
  target_compile_options(traceable_search_sort_lab_lib PRIVATE -Wall -Wextra -Wpedantic -Werror)
  target_compile_options(traceable_search_sort_lab PRIVATE -Wall -Wextra -Wpedantic -Werror)
  target_compile_options(traceable_search_sort_lab_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

add_test(NAME traceable_search_sort_lab_tests COMMAND traceable_search_sort_lab_tests)
