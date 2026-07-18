cmake_minimum_required(VERSION 3.20)

project(study_status VERSION 0.1.0 LANGUAGES CXX)

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

add_library(study_status_lib STATIC src/study_status.cpp)
target_include_directories(
  study_status_lib
  PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include"
)
target_compile_features(study_status_lib PUBLIC cxx_std_20)
set_target_properties(study_status_lib PROPERTIES CXX_EXTENSIONS OFF)
enable_project_warnings(study_status_lib)

add_executable(study_status_app src/main.cpp)
target_link_libraries(study_status_app PRIVATE study_status_lib)
enable_project_warnings(study_status_app)

include(CTest)

if(BUILD_TESTING)
  add_executable(study_status_tests tests/study_status_tests.cpp)
  target_link_libraries(study_status_tests PRIVATE study_status_lib)
  enable_project_warnings(study_status_tests)
  add_test(NAME study_status_tests COMMAND study_status_tests)
endif()
