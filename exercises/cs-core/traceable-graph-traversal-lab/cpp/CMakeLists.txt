cmake_minimum_required(VERSION 3.20)
project(traceable_graph_traversal_lab LANGUAGES CXX)

include(CTest)

add_library(traceable_graph_traversal_lab_lib src/lab.cpp)
target_include_directories(traceable_graph_traversal_lab_lib PUBLIC include)
target_compile_features(traceable_graph_traversal_lab_lib PUBLIC cxx_std_20)

add_executable(traceable_graph_traversal_lab src/main.cpp)
target_link_libraries(traceable_graph_traversal_lab PRIVATE traceable_graph_traversal_lab_lib)

add_executable(traceable_graph_traversal_lab_tests tests/test_lab.cpp)
target_link_libraries(traceable_graph_traversal_lab_tests PRIVATE traceable_graph_traversal_lab_lib)

if(MSVC)
  target_compile_options(traceable_graph_traversal_lab_lib PRIVATE /W4 /permissive-)
  target_compile_options(traceable_graph_traversal_lab PRIVATE /W4 /permissive-)
  target_compile_options(traceable_graph_traversal_lab_tests PRIVATE /W4 /permissive- /UNDEBUG)
else()
  target_compile_options(traceable_graph_traversal_lab_lib PRIVATE -Wall -Wextra -Wpedantic -Werror)
  target_compile_options(traceable_graph_traversal_lab PRIVATE -Wall -Wextra -Wpedantic -Werror)
  target_compile_options(traceable_graph_traversal_lab_tests PRIVATE -Wall -Wextra -Wpedantic -Werror -UNDEBUG)
endif()

add_test(NAME traceable_graph_traversal_lab_tests COMMAND traceable_graph_traversal_lab_tests)
