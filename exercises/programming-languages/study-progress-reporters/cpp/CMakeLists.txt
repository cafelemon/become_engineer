cmake_minimum_required(VERSION 3.20)

project(study_reporters VERSION 0.1.0 LANGUAGES CXX)

function(enable_project_warnings target_name)
  if(MSVC)
    target_compile_options(${target_name} PRIVATE /W4 /permissive-)
  else()
    target_compile_options(
      ${target_name}
      PRIVATE -Wall -Wextra -Wpedantic -Wconversion -Wshadow
    )
  endif()
endfunction()

add_library(study_report_lib STATIC src/study_report.cpp)
target_include_directories(
  study_report_lib
  PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include"
)
target_compile_features(study_report_lib PUBLIC cxx_std_20)
set_target_properties(study_report_lib PROPERTIES CXX_EXTENSIONS OFF)
enable_project_warnings(study_report_lib)

add_executable(study_report_app src/main.cpp)
target_link_libraries(study_report_app PRIVATE study_report_lib)
set_target_properties(study_report_app PROPERTIES CXX_EXTENSIONS OFF)
enable_project_warnings(study_report_app)

include(CTest)

if(BUILD_TESTING)
  add_executable(study_report_tests tests/study_report_tests.cpp)
  target_link_libraries(study_report_tests PRIVATE study_report_lib)
  set_target_properties(study_report_tests PROPERTIES CXX_EXTENSIONS OFF)
  enable_project_warnings(study_report_tests)
  add_test(NAME study_report_tests COMMAND study_report_tests)
endif()
