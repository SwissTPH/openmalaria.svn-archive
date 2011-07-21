package ch.swisstph.expcreator.exceptions;

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

import java.util.LinkedList;

/** Two patches overlap. Special handling to improve error reporting. */
public class PatchConflictException extends RuntimeException {

    public static final long serialVersionUID = 1L;	// avoid a warning (we don't need serialization...)
    private LinkedList<String> path;

    public PatchConflictException(String msg) {
        super(msg);
    path = new LinkedList<String>();
    }
    
    public void pushPath( String str ){
    path.addFirst( str );
}
    
    public String getMessage() {
    StringBuilder msg = new StringBuilder( "Patch conflict: " );
    for( String str : path ){
	msg.append( str );
    }
    msg.append( super.getMessage() );
        return msg.toString();
}
}