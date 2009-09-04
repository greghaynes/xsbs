subdirs(enet shared)

find_package(PythonLibs REQUIRED)
find_package(ZLIB REQUIRED)

set(xsbs_srcs
	engine/server.cpp
	engine/command.cpp

	fpsgame/server.cpp
	fpsgame/logging.cpp

	pycontrol/sbpy.cpp
	pycontrol/servermodule.cpp)

include(CheckFunctionExists)
include(CheckSymbolExists)

check_function_exists(gethostbyaddr_r, HAS_GETHOSTBYADDR_R)
check_function_exists(gethostbyname_r, HAS_GETHOSTBYNAME_R)
check_function_exists(poll, HAS_POLL)
check_function_exists(fcntl, HAS_FCNTL)
check_function_exists(inet_pton, HAS_INET_PTON)
check_function_exists(inet_ntop, HAS_INET_NTOP)

check_symbol_exists("struct msghdr.msg_flags" "sys/socket.h" HAS_MSGHDR_FLAGS)
check_symbol_exists("socklen_t" "sys/types.h;sys/socket.h" HAS_SOCKLEN_T)

add_definitions(-DSTANDALONE)

include_directories(${CMAKE_SOURCE_DIR}/src/engine
	${CMAKE_SOURCE_DIR}/src/fpsgame
	${CMAKE_SOURCE_DIR}/src/shared
	${CMAKE_SOURCE_DIR}/src/include
	${CMAKE_SOURCE_DIR}/src/pycontrol
	${CMAKE_SOURCE_DIR}/src/enet/include
	${PYTHON_INCLUDE_PATH}
	${ZLIB_INCLUDE_PATH})

add_executable(xsbs
	${xsbs_srcs})

target_link_libraries(xsbs enet sauertools ${PYTHON_LIBRARIES} ${ZLIB_LIBRARIES})
