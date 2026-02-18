import os
import argparse
import subprocess

def variant_calling_debreak(input_bam: str, output_dir: str, name: str) -> None:
    '''
    Performs variant calling with debreak

    Arguments
    ----------
    input_bam: str
        The input bam to run debreak with
    output_dir: str
        The output directory where to store the vcf files
    name: str
        The name of the sample that is being analyzed
    '''

    threads = 16

    realpath_input_bam = os.path.realpath(input_bam)

    subprocess.run(
        [
            "debreak",
            "--bam", realpath_input_bam,
            "--outpath", output_dir,
            "--thread", str(threads)
        ],
        check=True
    )

    # Rename variants.vcf to <name>.vcf 
    src = os.path.join(output_dir, "debreak.vcf")
    dst = os.path.join(output_dir, f"{name}.vcf")

    if os.path.exists(src):
        os.rename(src, dst)
    else:
        raise FileNotFoundError(f"DeBreak output file not found: {src}")



def main():
    
    parser = argparse.ArgumentParser(
        description="Run variant calling with deBreak."
    )

    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Sample or dataset name (used as an identifier for outputs)."
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory where output VCFs and intermediate files will be written."
    )

    # Linear alignment inputs
    parser.add_argument(
        "--data.linear.bam",
        dest="data_linear_bam",
        required=True,
        help="Linear-aligned BAM file for the dataset."
    )

    parser.add_argument(
        "--data.linear.bam.bai",
        dest="data_linear_bam_bai",
        required=True,
        help="Index (.bai) for the linear-aligned BAM file."
    )

    # Graph alignment inputs
    parser.add_argument(
        "--data.graph.bam",
        dest="data_graph_bam",
        required=True,
        help="Graph-aligned BAM file for the dataset."
    )

    parser.add_argument(
        "--data.graph.bam.bai",
        dest="data_graph_bam_bai",
        required=True,
        help="Index (.bai) for the graph-aligned BAM file."
    )

    parser.add_argument(
        "--data.gam",
        dest="data_gam",
        required=True,
        help="Graph Alignment Map (GAM) file for the dataset."
    )

    # Assembly inputs
    parser.add_argument(
        "--data.asm.hap1",
        dest="data_asm_hap1",
        required=True,
        help="Haplotype 1 assembly graph (GFA format)."
    )

    parser.add_argument(
        "--data.asm.hap2",
        dest="data_asm_hap2",
        required=True,
        help="Haplotype 2 assembly graph (GFA format)."
    )

    # Truth set
    parser.add_argument(
        "--data.truthset",
        dest="data_truthset",
        required=True,
        help="Truth set VCF (bgzipped) for benchmarking."
    )

    parser.add_argument(
        "--data.truthset.tbi",
        dest="data_truthset_tbi",
        required=True,
        help="Tabix index (.tbi) for the truth set VCF."
    )

    # Reference inputs
    parser.add_argument(
        "--data.reference",
        dest="data_reference",
        required=True,
        help="Reference genome FASTA file."
    )

    parser.add_argument(
        "--data.reference.fai",
        dest="data_reference_fai",
        required=True,
        help="FAI index for the reference genome FASTA."
    )

    # Workflow to follow
    parser.add_argument(
        "--workflow",
        dest="workflow",
        choices=["linear", "graph"],
        required=True,
        help=(
            "Select which BAM alignment to use for variant calling. "
            "'linear' uses --data.linear.bam, "
            "'graph' uses --data.graph.bam."
        )
    )

    args = parser.parse_args()

    if args.workflow == "linear":
        active_bam = args.data_linear_bam
        active_bam_bai = args.data_linear_bam_bai
    elif args.workflow == "graph":
        active_bam = args.data_graph_bam
        active_bam_bai = args.data_graph_bam_bai
    else:
        raise ValueError(f"Unsupported BAM mode: {args.workflow}")

    variant_calling_debreak(
        active_bam,
        args.output_dir,
        args.name
    )


if __name__ == "__main__":
    main()


