/* This file is part of OpenMalaria.
 * 
 * Copyright (C) 2005,2006,2007,2008 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 * 
 * OpenMalaria is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or (at
 * your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */


#include "Surface.h"
#include "SurfaceProvider.h"
#include "Font.h"
#include "macros.h"

Surface :: Surface(		int size,		unsigned int texture, 
											FontMM* font, SurfaceProvider* provider	)
:	font(font),
	size(size),
	texture(texture),
	provider(provider),
	linesInUse(0)
{
	charsPerLine = size/font->charSize.x;
	lineCount = size/(font->charSize.y + 1);

	ITERATE(i, lineCount)
	{
		lines.insert(lines.end(), new Line(this, (font->charSize.y + 1)*i));
	}
}

Surface :: ~Surface()
{
	ITERATE_LIST(Line*,lines,i,t, delete *i;)
	lines.clear();
}

void Surface :: unload()
{
	provider->remove(this, texture);
}
