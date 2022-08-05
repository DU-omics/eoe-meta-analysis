#shared
info_comparison_only_switch = """
	Switch on to plot exclusively the data belonging to the two conditions in the _Comparison dropdown_ within the main menu.
"""
info_hide_unselected_switch = """
	Before saving to picture, switch on to stop displaying unselected items.
"""
info_show_as_boxplots = """
	Switch on to produce box rather than violin plots.
"""
info_best_conditions_switch = """
	Switch on to plot only the most informative conditions.
"""
info_features_dropdown = """
	Select the features to plot, one by one.
	
	Click _Update plot_ when ready.
"""
info_features_search_area = """
	Write down the features to plot, separated by spaces, commas, semicolons. For microbial taxa and genes, please write them one per line as the names may contain these characters.

	Click _Search_ when ready.
"""
info_x_filter_dropdown_violins = """
	Choose the items within the _x_ axis.
"""
info_group_by = """
	Choose how to group the samples.
"""

#main dropdowns
info_analysis_dropdown = """
	Choose between different analysis branches.

	Every plot will be affected as new results will be loaded.
"""
info_expression_dropdown = """
	Choose between different expression datasets.

	_MDS_, _violin plots_, _heatmap_, and _MA plot_ will change accordingly.

	The _Expression profiling_ tab below will be populated accordingly.

	Select among different microbial __species__ to check for diversity in the tab below.
"""
info_feature_dropdown = """
	Choose the different feature to see its expression/abundance profile.

	_MDS_, _violin plot_ and _MA plot_ will change accordingly.
"""
info_comparison_filter_dropdown = """
	The string written in this box will be searched on both conditions and only those comparisons with the string on either side of the "vs" will be retained.

	Leave empty to show all comparisons. 
"""
info_comparison_dropdown = """
	Choose the comparison to see differential expression/abundance results, within the _MA plot_ and the resulting functional enrichment in the _GO plot_.

	The _Differential analysis_ tab below will be populated accordingly.
"""
info_best_comparison_switch = """
	Switch on to keep only the most informative comparisons within the _Comparison_ dropdown.
"""
info_stringency_dropdown = """
	Choose between analyses with different stringencies.

	The _MA plot_, _GO plot_, and statistics in _violin plots_ will be populated accordingly.
"""

#mds
info_dataset_dropdown_mds = """
	Choose between different expression datasets to see its multidimensional scaling.
"""
info_type_dropdown_mds = """
	Choose how to perform multidimensional scaling.
"""
info_color_by_dropdown_mds = """
	Choose the metadata to decorate the MDS.
"""
info_plot_mds = """
	Multidimensional scaling (MDS) visualization by low-dimensional embedding of high-dimensional data.
"""
info_x_violins = """
	Choose the metadata to use as x axis.
"""

#violins
info_y_violins = """
	Choose whether to see dispersion of log2 expression/abundance or any other continuous metadata.
"""
info_statistics_switch_violins = """
	Switch on to decorate the plot with statistics, if available.

	The expression/abundance _Statistics_ switch will be available only if _Condition_ is selected in both the _x_ and _Group by_ dropdowns, as this is calculated by DESeq. Differences according to any other variable present in the _y_ dropdown will be calculated by Mann–Whitney U test.

	Statistically significant comparisons (according to the _Stringency_ dropdown in the main menu) will be decorated with * between the two groups. For genes having more than one gene ID no statistics can be displayed and a # will appear instead.
"""

#ma plot
info_ma_plot = """
	MA plot showing differential expression/abundance analysis results, with average expression as a function of the fold change between conditions. Up- and down-regulated features are shown in red and blue, respectively.
"""
info_annotations_ma_plot = """
	Choose whether to display the _Differential analysis_ results, the _Selected feature_ in the Feature dropdown within the main menu, or both with _All_. 
"""

#go plot
info_go_plot_search_bar = """
	Use this to filter the categories shown.

	All keywords must be separated by spaces.

	Use "GO:" followed by ID to search for specific GO datasets.
"""
info_add_gsea_switch = """
	Add additional functional enrichment results calculated with GSEA.
"""
info_go_plot = """
	Balloon plot showing gene ontology (GO) functional enrichment results. Up- and down-regulated GO categories are shown in red and blue, respectively.

	Click the balloons to send the genes belonging to that GO category to the heatmap or the multi violin plots	within the _Expression profiling_ tab below.
"""

#analysis overview
info_sankey_plot = """
	Sankey diagram displaying numerosity and connections between the different relevant metadata.
"""

#heatmap
info_heatmap_annotation_dropdown = """
	Choose the metadata to be used to annotate the samples within the x axis.
	
	Click _Update plot_ when ready.
"""
info_heatmap_clustered_samples_switch = """
	Switch on to perform unsupervised hierarchical clustering of the samples within the x axis.
"""
info_heatmap_plot = """
	Heatmap showing row scaled log2 expression/abundance of the selected features.

	Features are shown along the y axis in accordance with unsupervised hierarchical clustering. Samples can also be cluastered using the _Clustered samples_ switch.
"""

#multiviolin
info_multiviolins_statistics_switch = """
	Switch on to decorate the plot with statistics, if available.

	The expression/abundance _Statistics_ switch will be available only if _Condition_ is selected in both the _x_ and _Group by_ dropdowns, as this is calculated by DESeq.

	Statistically significant comparisons (according to the _Stringency_ dropdown in the main menu) will be decorated with * between the two groups. For genes having more than one gene ID no statistics can be displayed and a # will appear instead.
"""

#correlation
info_correlation_x_dataset_dropdown = """
	Choose between different expression datasets to select the feature for the x axis.
"""
info_correlation_x_dropdown = """
	Choose the feature for the x axis.
"""
info_correlation_y_dataset_dropdown = """
	Choose between different expression datasets to select the feature for the y axis.
"""
info_correlation_y_dropdown = """
	Choose the feature for the y axis.
"""
info_correlation_sort_by_significance = """
	Switch on to sort the correlation results by statistical significance.
"""
info_correlation_statistics_plot = """
	Pearson correlation statistics.
"""

#species diversity
info_diversity_statistics_switch = """
	Switch on to calculate Mann–Whitney U statistics.
"""

#dge table
info_dge_table_feature_filter_dropdown = """
	Select specific features to create an extra handy filtered table on top.
"""
info_dge_table_target_prioritization_switch = """
	Switch on to perform target prioritization using the OpenTargets database.

	Differentially expressed genes will be ranked in accordance with
	i) having drugs already available,
	ii) being gentically associated with the disease (GWAS).
"""

#mofa
info_mofa_group_contrast_dropdown = """
	Choose between the different comparisons to see the associated results.
"""
info_mofa_data_overview_plot = """
	Heatmap showing which samples contributed to the analysis.
"""
info_mofa_variance_heatmap_plot = """
	Heatmap showing the percentage of variance explained by each layer in the two groups.

	Each factor correspond to a multi-omics molecular signature.

	Click into the heatmap to check the associated features within the _needle plot_ below. 
"""
info_mofa_top_features_for_factor_plot = """
	Needle plot showing the top (varying) features responsible for the factor in exam.

	Click into the heatmap per factor to check the associated features.

	Click the eye of a needle to check its expression/abundance within the _expression plots_ on the right. 
"""
info_mofa_group_condition_switch = """
	Switch off to divide samples by group rather than conditions. 
"""
info_mofa_factor_scores_plot = """
	Violin plots showing the distribution of the different factors within groups.

	Use the switch above the plot to divide samples by condition or group. 
"""
info_mofa_feature_expression_abundance_plot = """
	Violin plots showing the features selected by clicking the eye of the needles in the _Top feature plots_ on the left, here for your convenience.
"""

#deconvolution tab
info_deconvolution_split_by_dropdown = """
	Choose a metadata to use to divide the samples.
"""
info_deconvolution_and_by_2_dropdown = """
	Choose a metadata to use to divide the samples.
"""
info_deconvolution_and_by_3_dropdown = """
	Choose a metadata to use to divide the samples.
"""
info_deconvolution_data_sets_dropdown = """
	Choose which single-cell RNA-Seq dataset to be used for bulk RNA-Seq deconvolution.
"""
info_deconvolution_reset_labels_button = """
	Click to reset the labels created by clicking on any bar within the plot.
"""
