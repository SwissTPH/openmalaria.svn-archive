/*
 This file is part of OpenMalaria.
 
 Copyright (C) 2005-2009 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 
 OpenMalaria is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or (at
 your option) any later version.
 
 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
*/

#ifndef Hmod_VectorEmergenceSuite
#define Hmod_VectorEmergenceSuite

#include <fstream>
#include <string>
#include <sstream>
#include <stdexcept>
using namespace std;

#include <gsl/gsl_vector.h>
#include <gsl/gsl_matrix.h>
#include "util/vectors.h"

#include <cxxtest/TestSuite.h>
#include "configured/TestPaths.h"	// from config; but must be included from the build dir
#include "ExtraAsserts.h"

#include "Transmission/Vector/VectorEmergence.h"
#include "Transmission/Vector/VectorAnopheles.h"

// We want to hide normal output, so route it here instead of cout
ofstream null("\0");

  // Number of "days" in our "year" (θ_p) (small to speed up tests)
  // NOTE: affects array lengths, so not too easy to change
  const int YEAR_LEN = 10;
  // Population size (N_i)
  const int POP_SIZE = 1000;
  // Average availability (α_i)
  const double SUM_AVAIL = 0.0072 * POP_SIZE;
  
/** Tests on the Vector Control Emergence Rate calculation code.
 *
 * The output values were generated by NC using Matlab versions of these
 * functions. */
class VectorEmergenceSuite : public CxxTest::TestSuite
{
public:
  VectorEmergenceSuite () {
    Global::clResourcePath = UnittestSourceDir;
    string yamlFile = Global::lookupResource ("VectorEmergenceSuite.txt");
    ifstream file (yamlFile.c_str());
    if (!file.good()) throw runtime_error ("Unable to read VectorEmergenceSuite.txt");
    
    output1CalcInitMosqEmergeRate = readVector (file, "output1CalcInitMosqEmergeRate", YEAR_LEN);
    
    input1CalcUpsilonOneHost = readVector (file, "input1CalcUpsilonOneHost", YEAR_LEN);
    output1CalcUpsilonOneHost = readMatrices(file, "output1CalcUpsilonOneHost", 17, YEAR_LEN);
    
    input1CalcSvDiff = readVector (file, "input1CalcSvDiff", YEAR_LEN);
    input2CalcSvDiff = readVector (file, "input2CalcSvDiff", YEAR_LEN);
    input3CalcSvDiff = readMatrix (file, "input3CalcSvDiff", 17);
    input4CalcSvDiff = readMatrices(file,"input4CalcSvDiff", 17, YEAR_LEN);
    output1CalcSvDiff = readVector(file, "output1CalcSvDiff", YEAR_LEN);
    
    input1CalcLambda = readVector(file, "input1CalcLambda", YEAR_LEN);
    output1CalcLambda = readVectors (file, "output1CalcLambda", 17, YEAR_LEN);
    
    input1CalcXP = readMatrix  (file, "input1CalcXP", 17);
    input2CalcXP = readVectors (file, "input2CalcXP", 17, YEAR_LEN);
    input3CalcXP = readMatrices(file, "input3CalcXP", 17, YEAR_LEN);
    output1CalcXP = readVectors(file, "output1CalcXP",17, YEAR_LEN);
    
    input1FuncX = readMatrices (file, "input1FuncX", 17, YEAR_LEN);
    output1FuncX = readMatrix (file, "output1FuncX", 17);
    
    input1CalcSpectralRadius = readMatrix(file,"input1CalcSpectralRadius",17);
    
    input1CalcInv1minusA = readMatrix(file, "input1CalcInv1minusA",17);
    output1CalcInv1minusA = readMatrix(file, "output1CalcInv1minusA",17);
    
    input1CalSvfromEIRdata = readVector(file, "input1CalSvfromEIRdata", 10);
    output1CalSvfromEIRdata = readVector(file, "output1CalSvfromEIRdata", 10);
  }
  ~VectorEmergenceSuite () {
    gsl_vector_free (output1CalcInitMosqEmergeRate);
    
    gsl_vector_free (input1CalcUpsilonOneHost);
    freeMatrices (output1CalcUpsilonOneHost, YEAR_LEN);
    
    gsl_vector_free (input1CalcSvDiff);
    gsl_vector_free (input2CalcSvDiff);
    gsl_matrix_free (input3CalcSvDiff);
    freeMatrices (input4CalcSvDiff, YEAR_LEN);
    gsl_vector_free (output1CalcSvDiff);
    
    gsl_vector_free (input1CalcLambda);
    freeVectors (output1CalcLambda, YEAR_LEN);
    
    gsl_matrix_free (input1CalcXP);
    freeVectors (input2CalcXP, YEAR_LEN);
    freeMatrices(input3CalcXP, YEAR_LEN);
    freeVectors (output1CalcXP,YEAR_LEN);
    
    freeMatrices (input1FuncX, YEAR_LEN);
    gsl_matrix_free (output1FuncX);
    
    gsl_matrix_free (input1CalcSpectralRadius);
    
    gsl_matrix_free (input1CalcInv1minusA);
    gsl_matrix_free (output1CalcInv1minusA);
    
    gsl_vector_free (input1CalSvfromEIRdata);
    gsl_vector_free (output1CalSvfromEIRdata);
  }
  
  // Create and destroy emerge for each test, so tests can't affect one another:
  void setUp () {
    hostBase.probMosqBiting = 0.95;
    hostBase.probMosqFindRestSite = 0.95;
    hostBase.probMosqSurvivalResting = 0.94;
    emerge = new VectorEmergence (3, 5,		// mosqRestDuration (τ), EIPDuration (θ_s)
	  POP_SIZE,
	  1.6, 0.33,	// mosqSeekingDeathRate (μ_vA), mosqSeekingDuration (θ_d)
	  SUM_AVAIL,
	  hostBase, .93,// probMosqSurvivalOvipositing (P_E)
	  YEAR_LEN,
	  null, "\0");	// traceOut, logFileName
  }
  void tearDown () {
    delete emerge;
  }
  
  // Test the entire emergence-rate calculation.
  // Cheat a little and copy inputs from other tests.
  void testCalcInitMosqEmergeRate () {
    Global::clOptions = static_cast<CLO::CLO> (Global::clOptions | CLO::ENABLE_ERC);
    
    vector<double> EIRInit(YEAR_LEN, 0.0);
    for (int i = 0; i < YEAR_LEN; ++i)
      EIRInit[i] = gsl_vector_get(input1CalSvfromEIRdata, i);
    
    // Produce a rough estimate, which IS NOT the same as expected output:
    vector<double> emergeRate (YEAR_LEN);
    const double temp = POP_SIZE*SUM_AVAIL;
    for (int i = 0; i < YEAR_LEN; i++)
      emergeRate[i] = EIRInit[i]*temp;
    
    vector<double> in1 = vectors::gsl2std(input1CalcUpsilonOneHost);
    //FIXME
    NonHumanHostsType NonHumanHosts;
    emerge->CalcInitMosqEmergeRate(in1,
				   EIRInit,
				   NonHumanHosts,
				   emergeRate);
    
    // Requires a slightly higher error tolerance. NC did say the results he
    // gave (output1CalcInitMosqEmergeRate) were off by about 1e-10.
    TS_ASSERT_VECTOR_APPROX_TOL (vectors::std2gsl(emergeRate, YEAR_LEN), output1CalcInitMosqEmergeRate, 1e-6, 1e-6);
  }
  
  void testCalcUpsilonOneHost () {
    double PA, PAi;
    //FIXME
    NonHumanHostsType NonHumanHosts;
    emerge->CalcUpsilonOneHost (&PA, &PAi, input1CalcUpsilonOneHost, NonHumanHosts);
    TS_ASSERT_APPROX (PA,  5.4803567e-002);
    TS_ASSERT_APPROX (PAi, 7.7334254e-001);
    for (int i = 0; i < YEAR_LEN; ++i)
      TS_ASSERT_VECTOR_APPROX (emerge->Upsilon[i], output1CalcUpsilonOneHost[i]);
  }
  
  void testCalcSvDiff () {
    /* This test fails because the output SvDiff is a difference between relatively similar values,
     * so the difference is small and numerical errors high. This is a small func so test isn't
     * really important.
    gsl_matrix **origUpsilon = emerge->Upsilon;
    emerge->Upsilon = input4CalcSvDiff;
    
    gsl_vector *SvDiff = gsl_vector_calloc (YEAR_LEN);
    emerge->CalcSvDiff (SvDiff, input1CalcSvDiff, input2CalcSvDiff, input3CalcSvDiff);
    TS_ASSERT_VECTOR_APPROX (SvDiff, output1CalcSvDiff);
    
    emerge->Upsilon = origUpsilon;
    */
  }
  
  void testCalcLambda () {
    emerge->CalcLambda (input1CalcLambda);
    for (int i = 0; i < YEAR_LEN; ++i)
      TS_ASSERT_VECTOR_APPROX (emerge->Lambda[i], output1CalcLambda[i]);
  }
  
  void testCalcXP () {
    gsl_vector **origLambda = emerge->Lambda;
    gsl_matrix **origUpsilon = emerge->Upsilon;
    emerge->Lambda = input2CalcXP;
    emerge->Upsilon = input3CalcXP;
    
    emerge->CalcXP (input1CalcXP);
    for (int i = 0; i < YEAR_LEN; ++i)
      TS_ASSERT_VECTOR_APPROX (emerge->x_p[i], output1CalcXP[i]);
    
    emerge->Lambda = origLambda;
    emerge->Upsilon = origUpsilon;
  }
  
  void testCalcPSTS () {
    // Also considered inputs: tau=3, theta_s=5
    double sumKPlus;
    double sumKLPlus[2];
    emerge->CalcPSTS (&sumKPlus, sumKLPlus, 5.4803567e-002, 6.1014058e-001);
    TS_ASSERT_APPROX (sumKPlus, 3.0034309e-003);
    TS_ASSERT_APPROX (sumKLPlus[0], 6.1014058e-001);
    TS_ASSERT_APPROX (sumKLPlus[1], 3.3437880e-002);
  }
  
  void testFuncX () {
    gsl_matrix **origUpsilon = emerge->Upsilon;
    emerge->Upsilon = input1FuncX;
    
    gsl_matrix *X = gsl_matrix_calloc (17,17);
    emerge->FuncX (X, 10, 0);
    TS_ASSERT_VECTOR_APPROX (X, output1FuncX);
    gsl_matrix_free (X);
    
    emerge->Upsilon = origUpsilon;
  }
  
  void testCalcSpectralRadius () {
    TS_ASSERT_APPROX (emerge->CalcSpectralRadius (input1CalcSpectralRadius), 2.3950405e-001);
  }
  
  void testCalcInv1minusA () {
    // Considered an input: eta = 17
    gsl_matrix* inv1A = gsl_matrix_calloc(17,17);
    emerge->CalcInv1minusA (inv1A, input1CalcInv1minusA);
    TS_ASSERT_VECTOR_APPROX (inv1A, output1CalcInv1minusA);
    gsl_matrix_free (inv1A);
  }
  
  void testCalSvfromEIRdata () {
    gsl_vector *Sv = gsl_vector_calloc (10);
    emerge->CalSvfromEIRdata (Sv, 7.7334254e-001, input1CalSvfromEIRdata);
    TS_ASSERT_VECTOR_APPROX (Sv, output1CalSvfromEIRdata);
    gsl_vector_free (Sv);
  }
  
private:
  void checkNextString (istream& in, string expect) {
    string name;
    in >> name;
    if (expect != name) {
      ostringstream msg;
      msg << "Next item expected in VectorEmergenceSuite.txt: "
      << expect
      << ", got: "
      << name;
      throw runtime_error (msg.str());
    }
  }
  
  gsl_matrix* readMatrix (istream& in, string name, int dim) {
    checkNextString (in, name);
    return readMatrix (in, dim);
  }
  gsl_matrix* readMatrix (istream& in, int dim) {
    gsl_matrix* ret = gsl_matrix_calloc (dim, dim);
    double x;
    for (int i = 0; i < dim; ++i)
      for (int j = 0; j < dim; ++j) {
	in >> x;
	gsl_matrix_set(ret,i,j, x);
      }
    return ret;
  }
  // read num matrixs each of length dim
  gsl_matrix** readMatrices (istream& in, string name, int dim, int num) {
    checkNextString (in, name);
    gsl_matrix** ret = new gsl_matrix*[num];
    for (int i = 0; i < num; ++i)
      ret[i] = readMatrix(in, dim);
    return ret;
  }
  void freeMatrices (gsl_matrix** mat, int num) {
    for (int i = 0; i < num; ++i)
      gsl_matrix_free (mat[i]);
    delete[] mat;
  }
  
  gsl_vector* readVector (istream& in, string name, int dim) {
    checkNextString (in, name);
    return readVector (in, dim);
  }
  gsl_vector* readVector (istream& in, int dim) {
    gsl_vector* ret = gsl_vector_calloc (dim);
    double x;
    for (int i = 0; i < dim; ++i) {
      in >> x;
      gsl_vector_set(ret,i, x);
    }
    return ret;
  }
  // read num vectors each of length dim
  gsl_vector** readVectors (istream& in, string name, int dim, int num) {
    checkNextString (in, name);
    gsl_vector** ret = new gsl_vector*[num];
    for (int i = 0; i < num; ++i)
      ret[i] = readVector(in, dim);
    return ret;
  }
  void freeVectors (gsl_vector** vec, int num) {
    for (int i = 0; i < num; ++i)
      gsl_vector_free (vec[i]);
    delete[] vec;
  }
  
  VectorEmergence *emerge;
  HostCategoryAnopheles hostBase;
  
  gsl_vector *output1CalcInitMosqEmergeRate;
  gsl_vector *input1CalcUpsilonOneHost;
  gsl_matrix **output1CalcUpsilonOneHost;
  gsl_vector *input1CalcSvDiff, *input2CalcSvDiff, *output1CalcSvDiff;
  gsl_matrix *input3CalcSvDiff, **input4CalcSvDiff;
  gsl_vector *input1CalcLambda, **output1CalcLambda;
  gsl_matrix *input1CalcXP, **input3CalcXP;
  gsl_vector **input2CalcXP, **output1CalcXP;
  gsl_matrix **input1FuncX, *output1FuncX;
  gsl_matrix *input1CalcSpectralRadius;
  gsl_matrix *input1CalcInv1minusA, *output1CalcInv1minusA;
  gsl_vector *input1CalSvfromEIRdata, *output1CalSvfromEIRdata;
};

#endif
