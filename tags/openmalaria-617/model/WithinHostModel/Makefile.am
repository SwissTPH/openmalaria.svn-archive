noinst_LIBRARIES = libWithinHostModel.a

libWithinHostModel_a_SOURCES = Descriptive.cpp OldIPT.cpp Dummy.cpp\
  Infection.cpp DescriptiveInfection.cpp DummyInfection.cpp OldIPTInfection.cpp

AM_CPPFLAGS = @CPPFLAGS@ @BOINC_CFLAGS@ -I@top_builddir@/xsdcxx -I$(top_srcdir)/include
AM_CXXFLAGS = @CXXFLAGS@ -static-libgcc -Wall #-Werror 

clean: clean-am clean-scenario

clean-scenario:
	rm -f scenario.cxx scenario.hxx scenario.ixx
