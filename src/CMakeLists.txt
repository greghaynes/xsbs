subdirs(enet)

find_package(PythonLibs REQUIRED)

set(xsbs_srcs
	engine/server.cpp
	engine/command.cpp

	fpsgame/server.cpp

	shared/crypto.cpp
	shared/stream.cpp
	shared/tools.cpp
	
	pycontrol/pluginmanager.cpp
	pycontrol/plugin.cpp
	pycontrol/eventtable.cpp)

add_definitions(-DSTANDALONE)

include_directories(engine fpsgame shared include pycontrol enet/include ${PYTHON_INCLUDE_PATH})

add_executable(xsbs
	${xsbs_srcs})

target_link_libraries(xsbs enet z)
