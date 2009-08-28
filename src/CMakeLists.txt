set(xsbs_srcs
	engine/server.cpp
	engine/command.cpp

	fpsgame/server.cpp

	shared/crypto.cpp
	shared/stream.cpp
	shared/tools.cpp)

add_library(enet STATIC IMPORTED)
set_property(TARGET enet PROPERTY IMPORTED_LOCATION ${CMAKE_SOURCE_DIR}/src/enet/libenet.a)

add_definitions(-DSTANDALONE)

include_directories(engine fpsgame shared enet/include)

add_executable(xsbs
	${xsbs_srcs})

target_link_libraries(xsbs enet)
