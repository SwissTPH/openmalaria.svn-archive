# CMake configuration for all code in this dir and below
# Copyright © 2005-2009 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
# Licence: GNU General Public Licence version 2 or later (see COPYING)

# Don't use aux_source_directory on . because we don't want to compile openMalaria.cpp in to the lib.
set (Model_CPP
  Simulation.cpp
  Global.cpp
  Population.cpp
  PopulationAgeStructure.cpp
  PopulationStats.cpp
  inputData.cpp
  ${CMAKE_CURRENT_BINARY_DIR}/scenario.cxx
  
  Host/Human.cpp
  Host/InfectionIncidenceModel.cpp
  Host/NeonatalMortality.cpp
  Host/Vaccine.cpp
  Host/ContinuousIntervention.cpp
  
  Clinical/ClinicalModel.cpp
  Clinical/CaseManagementCommon.cpp
  Clinical/EventScheduler.cpp
  Clinical/ESCaseManagement.cpp
  Clinical/ESDecisionTree.cpp
  Clinical/ESDecisionValue.cpp
  Clinical/ImmediateOutcomes.cpp
  Clinical/OldCaseManagement.cpp
  Clinical/Episode.cpp
  Clinical/parser.cpp
  
  Pathogenesis/PathogenesisModel.cpp
  Pathogenesis/Mueller.cpp
  Pathogenesis/Pyrogen.cpp
  Pathogenesis/Predet.cpp
  
  PkPd/PkPdModel.cpp
  #PkPd/HoshenPkPdModel.cpp
  PkPd/LSTMPkPdModel.cpp
  #PkPd/Drug/HoshenDrug.cpp
  #PkPd/Drug/HoshenDrugType.cpp
  PkPd/Drug/LSTMDrug.cpp
  PkPd/Drug/LSTMDrugType.cpp
  #PkPd/Proteome.cpp
  
  Transmission/TransmissionModel.cpp
  Transmission/NonVector.cpp
  Transmission/PerHostTransmission.cpp
  Transmission/Vector/VectorTransmission.cpp
  Transmission/Vector/VectorAnopheles.cpp
  Transmission/Vector/HostCategoryAnopheles.cpp
  Transmission/Vector/HostCategoryAnophelesHumans.cpp
  Transmission/Vector/HostCategoryAnophelesNonHumans.cpp
  
  WithinHost/WithinHostModel.cpp
  WithinHost/CommonWithinHost.cpp
  WithinHost/DescriptiveWithinHost.cpp
  WithinHost/DescriptiveIPTWithinHost.cpp
  WithinHost/Infection/Infection.cpp
  WithinHost/Infection/DescriptiveInfection.cpp
  WithinHost/Infection/DescriptiveIPTInfection.cpp
  WithinHost/Infection/DummyInfection.cpp
  WithinHost/Infection/EmpiricalInfection.cpp
  WithinHost/Infection/MolineauxInfection.cpp
  
  util/BoincWrapper.cpp
  util/timer.cpp
  util/gsl.cpp
  util/vectors.cpp
  util/WeibullDecayedValue.cpp
  util/errors.cpp
  util/checkpoint.cpp
  util/ModelOptions.cpp
  util/CommandLine.cpp
  util/random.cpp
  util/StreamValidator.cpp
  util/AgeGroupInterpolation.cpp
  
  Monitoring/Continuous.cpp
  Monitoring/Surveys.cpp
  Monitoring/Survey.cpp
)

# Headers - only included so they show up in IDEs:
file (GLOB_RECURSE Model_H "${CMAKE_SOURCE_DIR}/include/*.h")

set (XSD_FILE ${CMAKE_SOURCE_DIR}/schema/scenario.xsd)
add_custom_command (
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/scenario.cxx ${CMAKE_CURRENT_BINARY_DIR}/scenario.ixx ${CMAKE_CURRENT_BINARY_DIR}/scenario.hxx
  COMMAND ${XSD_EXECUTABLE} cxx-tree
      --type-naming ucc --function-naming java
      --namespace-map =scnXml
      --generate-serialization --generate-inline
      --generate-doxygen --generate-intellisense
      ${XSD_FILE}
  MAIN_DEPENDENCY ${XSD_FILE}
  COMMENT "Compiling ${XSD_FILE}"
  VERBATIM
)


include_directories (SYSTEM
  ${XSD_INCLUDE_DIRS}
  ${XERCESC_INCLUDE_DIRS}
  ${GSL_INCLUDE_DIRS}
  ${Z_INCLUDE_DIRS}
  ${Boost_INCLUDE_DIRS}
  ${SPIRIT_INCLUDE_DIRS}

  ${CMAKE_SOURCE_DIR}/contrib/gzstream
  ${CMAKE_SOURCE_DIR}/contrib/FastDelegate_src
  ${CMAKE_SOURCE_DIR}/contrib/floating_point_utilities_v3
)
include_directories (
  ${CMAKE_SOURCE_DIR}/include ${CMAKE_BINARY_DIR}/model
)

add_library (model
  ${Model_CPP}
  ${Model_H}
  ${CMAKE_CURRENT_BINARY_DIR}/scenario.ixx ${CMAKE_CURRENT_BINARY_DIR}/scenario.hxx
)

if (MSVC)
  set_target_properties (model PROPERTIES
    LINK_FLAGS "${OM_LINK_FLAGS}"
    COMPILE_FLAGS "${OM_COMPILE_FLAGS}"
  )
endif (MSVC)
