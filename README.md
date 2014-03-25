<h1>Model2roms</h1>

This project is a Python toolbox for creating the necessary climatology, boundary, and initial files 
required to run the ROMS (Regional Ocean Modeling System) model. As a first version this toolkit focus on 
converting the SODA, HYCOM, or GLORYS (Mercator Ocean) model runs to a set of forcing files for a given ROMS 
grid structure.

<h2>Background</h2>

For the last year I have been working on this toolbox that I used to call soda2roms, but which is now 
renamed to model2roms as it has become more generic over the years. This program is a collection of python 
and Fortran modules that can be used to create climatology (CLIM), initial (INIT), and boundary (BRY) files 
necessary to run the ROMS model. Currently, the program takes rectangular gridded forcing filesinput at 
Z-levels. These data are interpolated to the ROMS grid at Z-levels. Then the Z-levels are interpolated 
vertically to the sigma layers. For U, and V velocities, the interpolation is done at RHO points, and then 
interpolated to U and V points. All interpolated values are written to netCDF4 files, where the result is one 
file for each CLIM, INIT, and BRY files. UBAR and VBAR are calculated from U and V. Time is stored as julian 
day from 01/01/1948 (see soda2roms.py).

```html
python main.py
```

<h2>Contact</h2>
<ul>
<li>me @ trondkristiansen.com</li>
<li>http://github.com/trondkr</li>
<li>www.trondkristiansen.com</li>
</ul>
Please send a comment on suggestions, questions, or modifications and improvements you would like to
make to me @ trondkristiansen.com. I would very much like to see this project go much further so that it can be
useful for a variety of purposes.

<h2>License</h2>

Model2roms is available under the MIT license. See the LICENSE file for more info.