package ch.swisstph.expcreator.utils;

/**
 * experiment_creator: An experiment creation tool for openmalaria
 * Copyright (C) 2005-2010 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.*/

import java.io.File;
import java.io.FilenameFilter;

public class XMLFileFilter implements FilenameFilter {

    private boolean isBase;

    public XMLFileFilter(boolean isBase) {
        this.isBase = isBase;
    }

    @Override
    public boolean accept(File dir, String name) {
        if (isBase) {
            return name.equals("base.xml");
        }
        return name.endsWith(".xml");
    }
}
