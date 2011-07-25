package ch.swisstph.expcreator.arms;

import java.io.File;

import org.w3c.dom.Document;

public class DummyArm extends Arm {

    public DummyArm(String name) {
        super(name);
    }

    public void writePatch(File dir) throws Exception {
        // empty
    }

    public Document apply(Document document) throws Exception {
        return null;
    }

}
