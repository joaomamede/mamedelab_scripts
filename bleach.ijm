for (i=1;i<11;i++) {
	selectWindow("igfp1_caruby5_VOG004_v"+i+"_PRJcorrected.ome.tiff");
	run("Bleach Correction", "correction=[Simple Ratio] background=120");
	run("OME-TIFF...", "save=/run/media/jmamede/Joao/CAruby/20200629/igfp1_caruby5_VOG004_v"+i+"_PRJcorrected_unbleach.ome.tiff compression=LZW");
	close();
	selectWindow("igfp1_caruby5_VOG004_v"+i+"_PRJcorrected.ome.tiff");
	close();
}

