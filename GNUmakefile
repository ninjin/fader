# Build external tools and resources
#
# Author:	Pontus Stenetorp	<pontus stenetorp se>
# Version:	2012-09-12

EXT_DIR=ext

SIMSTRING_DIR=${EXT_DIR}/simstring
SIMSTRING_PY_DIR=${SIMSTRING_DIR}/swig/python
# We are excessive in what we count as a dependency, but that should be fine
SIMSTRING_DEPS=${shell find ${SIMSTRING_DIR}/ -type d}
SIMSTRING_BIN=${SIMSTRING_DIR}/simstring

# We include the Python bindings here for now
${SIMSTRING_BIN}: ${SIMSTRING_DEPS}
	cd ${SIMSTRING_DIR} && \
		./configure && \
		make
	cd ${SIMSTRING_PY_DIR} && \
		./prepare.sh && \
		python setup.py build_ext --inplace -liconv && \
		python -c 'import simstring'
	touch ${SIMSTRING_BIN}

.PHONY: clean
clean:
	cd ${SIMSTRING_DIR} && make clean
	cd ${SIMSTRING_PY_DIR} && \
		python setup.py clean && \
		rm -f _simstring.so
