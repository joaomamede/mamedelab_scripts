for (i=1;i<11;i++) {
	selectWindow("igfp1_caruby5_VOG005_onlyPBS_v"+i+"_PRJ.ome.tiff");
	run("Correct Drift", "choose=/run/media/jmamede/Joao/CAruby/20200630/igfp1_caruby5_VOG005_onlyPBS_v1_PRJ.omeDriftTable.njt");
	run("OME-TIFF...", "save=/run/media/jmamede/Joao/CAruby/20200630/igfp1_caruby5_VOG005_onlyPBS_v"+i+"_PRJcorrected.ome.tiff compression=LZW");
	close();
	selectWindow("igfp1_caruby5_VOG005_onlyPBS_v"+i+"_PRJ.ome.tiff");
	close();
}