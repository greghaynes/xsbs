project(sauertools)

set(sauertools_srcs
	tools.cpp
	stream.cpp
	crypto.cpp)

add_library(sauertools STATIC ${sauertools_srcs})
