// MIXER GEOMETRY (merge)
// Valérie Bibeau, Polytechnique Montréal
// 2020

SetFactory("OpenCASCADE");

// -------------------------------------------
// Dimensionless geometry variables
// -------------------------------------------

T = 1;

ratioTD = {{ratioTD}};
  D = T/ratioTD;
ratioHT = {{ratioHT}};
  H = T*ratioHT;
ratioTC = {{ratioTC}};
  C = T/ratioTC;
ratioDW = {{ratioDW}};
  W = D/ratioDW;
ratioDW = {{ratioDW_Hub}};
  W_Hub = D/ratioDW;

theta = -{{theta}};

H_blade = W;
E = {{p_thick}}*W;

// -------------------------------------------
// Cylinder (tank)
// -------------------------------------------
Cylinder(1) = {0, 0, 0, 0, 0, H, T/2, 2*Pi};

// -------------------------------------------
// Cylinder (pbt)
// -------------------------------------------
Cylinder(2) = {0, 0, C, 0, 0, H, W/2, 2*Pi};

// -------------------------------------------
// Cylinder (pbt hub)
// -------------------------------------------
Cylinder(3) = {0, 0, C, 0, 0, H_blade, W_Hub/2, 2*Pi};

// -------------------------------------------
// Blade 1
// -------------------------------------------
Box (4) = { 0, -E/2, C, D/2, E, H_blade };
Rotate { { 1,0,0 }, {0, 0, C+H_blade/2}, -theta } {Volume{4};}

// -------------------------------------------
// Blade 2
// -------------------------------------------
Box (5) = { -E/2, -D/2, C, E, D/2, H_blade };
Rotate { { 0,1,0 }, {0, 0, C+H_blade/2}, theta } {Volume{5};}

// -------------------------------------------
// Blade 3
// -------------------------------------------
Box (6) = { -E/2, 0, C, E, D/2, H_blade };
Rotate { { 0,1,0 }, {0, 0, C+H_blade/2}, -theta } {Volume{6};}

// -------------------------------------------
// Blade 4
// -------------------------------------------
Box (7) = { 0, -E/2, C, -D/2, E, H_blade };
Rotate { { 1,0,0 }, {0, 0, C+H_blade/2}, theta } {Volume{7};}

// -------------------------------------------
// Volume (fluid - shaft)
// -------------------------------------------
BooleanDifference{ Volume{1}; Delete; }{ Volume{2:7}; Delete; }

// -------------------------------------------
// Attractor field
// -------------------------------------------
Field[1] = Attractor;
Field[1].EdgesList = {14:17,22,26,30,31,36,40,44:49,53:200};
Field[2] = Threshold;
Field[2].IField = 1;
Field[2].LcMin = {{min_mesh_length}};
Field[2].LcMax = {{max_mesh_length}};
Field[2].DistMin = (T-D)/20;
Field[2].DistMax = (T-D)/4;
Background Field = 2;

// -------------------------------------------
// Boundary conditions
// -------------------------------------------
Physical Surface(0) = {1:28,32:1000}; // Wall
Physical Surface(1) = {29}; // Wall
Physical Surface(2) = {30}; // Top
Physical Surface(3) = {31}; // Bottom

Physical Volume(0) = {1:100};
