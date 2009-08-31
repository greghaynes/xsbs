subdirs(enet shared)

find_package(PythonLibs REQUIRED)

set(xsbs_srcs
	engine/server.cpp
	engine/command.cpp

	fpsgame/server.cpp

	pycontrol/sbpy.cpp)

add_definitions(-DSTANDALONE)

include_directories(${CMAKE_SOURCE_DIR}/src/engine
	${CMAKE_SOURCE_DIR}/src/fpsgame
	${CMAKE_SOURCE_DIR}/src/shared
	${CMAKE_SOURCE_DIR}/src/include
	${CMAKE_SOURCE_DIR}/src/pycontrol
	${CMAKE_SOURCE_DIR}/src/enet/include
	${PYTHON_INCLUDE_PATH})

add_executable(xsbs
	${xsbs_srcs})

target_link_libraries(xsbs enet sauertools z ${PYTHON_LIBRARIES})
