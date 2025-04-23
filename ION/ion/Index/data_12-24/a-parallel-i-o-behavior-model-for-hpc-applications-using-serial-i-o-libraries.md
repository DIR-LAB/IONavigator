# A parallel I/O behavior model for HPC applications using serial I/O libraries

Pilar Gomez-Sanchez∗ , Sandra Mendez† , Dolores Rexachs∗ and Emilio Luque∗

∗Computer Architecture and Operating Systems Department

Universitat Autonoma de Barcelona ´

Barcelona, Spain

Email: {pilar.gomez, dolores.rexachs, emilio.luque}@uab.es

†High Performance Systems Division

Leibniz Supercomputing Centre (LRZ)

Garching bei Mnchen, Germany

Email: sandra.mendez@lrz.de

*Abstract*—Analyzing and understanding an application's Input/Output (I/O) access patterns provides key information to gain insight into how the behavior of an application affects its performance in different systems. In this paper, we propose a portable model to represent the I/O behavior of parallel applications that use serial I/O libraries, as part of a more holistic model for I/O of parallel applications. The model allows actions such as replication of the application behavior on different HPC systems and evaluation of the I/O performance without running the real application. In this paper, we evaluate the portability of the proposed model for MADbench2 and ABYSS-P in four HPC systems. We analyze the impact of the parallel system configuration in a Cloud environment for the ABYSS-P application by using the proposed I/O behavior model.

*Keywords*—HPC Systems, Parallel I/O, I/O model, I/O Phase, POSIX-IO.

#### I. INTRODUCTION

Identifying the root cause of possible I/O bottlenecks and poor performance requires understanding the I/O patterns of parallel applications and their interaction with the I/O system. The I/O pattern used for the application renders important information, not only regarding how its behavior affects the application performance but also it allows us to select the hardware and software resources that are required by the application and evaluate different I/O configurations.

In this context, we propose a holistic I/O behavior model that represents the I/O patterns of a parallel application independent of the I/O system.

Most scientific parallel applications are repetitive, where similar behavior can be observed during the execution time. These applications have similar portions that commonly are named phases, which usually have a homogeneous behavior. We define our model based on the I/O phases, because the repetitive property is also applied to I/O operations in files.

In a previous work [1], our research group proposed a behavior model to represent the access pattern of parallel scientific applications that use parallel I/O libraries.

In the present paper we redefine the model to include parallel scientific applications that use serial I/O libraries and we redefine the I/O phase concept. Observing the I/O behavior of the application in two layers allows us to analyze and understand how the application is executed in each layer.

Once the I/O model is obtained, it customizes a synthetic program or the IOR [2] benchmark to replicate the I/O kernel of application, which is executed in another system or in another I/O configuration without executing the real application.

Our main contribution is summarized as follows:

- We define a portable model named PIOM-PX, which describes the parallel I/O behavior of HPC applications when using serial libraries based on I/O phases.
- We validate the portability of the model on four different I/O systems.
- We analyze the impact of the parallel file system configuration in a Cloud environment for the ABYSS-P application [3] by using the proposed I/O behavior model.

This paper is organized as follows. Section II presents the related work. Section III describes the proposed I/O model. In Section IV, we validate the proposed I/O model and in Section V, we present a use case. Finally, in Section VI, we explain our conclusions and future work.

#### II. RELATED WORK

Understanding the I/O behavior of parallel applications is essential for I/O performance evaluation. The behavior is represented by access patterns in the different files of the application. Several authors present different approaches to extract I/O patterns, understanding them and using them to propose new techniques to improve I/O performance.

Byna et al. [4] present a classification of I/O patterns focusing on the local patterns of each process. They use an I/O-signature to describe the sequence of I/O accesses in a pattern for every trace file. The I/O signature allows their select caching and prefetching optimization strategies. He et al. [5] propose different techniques to discover the access pattern using the Markov model in an unstructured I/O. They build a prototype file system with pattern-aware prefetching to reduce

![](_page_1_Figure_0.png)

Figure 1. Description of steps to extract the application I/O behavior model.

the I/O latency. The main difference between those works and ours is the layer where the analysis is carried out, the MPI-IO layer. In our case, we analyse at the POSIX layer. Besides, we analyze the applications that use serial I/O libraries. Another difference is that we extract the application I/O behavior in order to understand the impact over the I/O system.

Kluge et al. [6] extract the application I/O pattern for detecting serialization points in applications, to create a I/O benchmark for later selecting the best file system or estimating the I/O performance in another HPC system. Behzad et al. [7], [8] develop a framework to extract the I/O pattern at HDF5 layer to obtain the optimal configuration of the I/O system [9] by selecting the best set of parameters of I/O Software Stack for a specific application. Unlike these work, we focus on modelling the I/O behavior at the POSIX-IO based on I/O phases, their repetitions and their weight.

Mendez et al. [1] present an I/O behavior model of application based on the phase concept and defined by the metadata, spatial global pattern and temporal global pattern. The analysis is carried out at the MPI-IO layer. In this paper, we present an extension of their work, we analyze the I/O behavior of the application at the POSIX-IO level. By analyzing at this level, we capture I/O operations performed for parallel and serial I/O libraries.

Our main difference with previously mentioned papers is that we propose an I/O model for parallel applications at POSIX-IO level based on I/O phases. We explore the application's I/O behavior at POSIX layer to obtain the behavior at serial I/O libraries layer. This model allows us to replicate the application's I/O behavior in other HPC systems.

#### III. PROPOSED I/O MODEL

Most scientific parallel applications exhibit a repetitive behavior. Considering this characteristic, we define an I/O behavior model based on the I/O phases. A set of I/O concepts are defined at parallel application, file and I/O phase level, which are used to represent the proposed model. These are selected to obtain the spatial pattern, temporal pattern and data volume to be transferred by a parallel application.

We extract the I/O model concepts following the steps presented in Figure 1, which are automated. In step 1, the application is traced to register the POSIX-IO operations, and the communication and I/O MPI events. Due to this, the I/O model must be independent of the underlying I/O system, the I/O pattern extraction must only consider the I/O properties that can be portable to other systems. In steps 2-3, each trace file is analyzed to extract the I/O concepts. In step 4, the I/O model is obtained.

### *A. Concepts at Parallel Application Level*

HPC applications implement different I/O strategies, which are related to the access type in files. Usually, these I/O strategies for an MPI application that uses npapp processes can be classified in: i) 1 file per process; ii) a single shared file for np processes and iii) a single shared file for N processes, where N is a subset of np processes.

The number of files (NFiles) opened by a MPI application during the execution time and the size of these files allow it to know the capacity storage required (STapp). In Table I, we describe the concepts defined to obtain the I/O behavior.

#### *B. Concepts at File Level*

A file has three main characteristics: access mode, file access type and size.

Access mode is related to the offset of the I/O operations in the file. In addition, it is identified based on the displacement between two consecutive I/O operations. Considering a total of N I/O operations for a file, the access mode can be among the following: sequential (if ∀ operations, displacement is equal to request size and the offsets are consecutive), strided (if ∀ operations, displacement is equal to request size and the offsets are not consecutive) and random ( if ∀ operations, displacement is variable). Instead, File Access Type depends on the open mode that can be read only, write only or write/read.

In the context of a parallel application, a file can be opened for np processes, therefore we need to consider another characteristic that is called Access Type, which is related to the number of processes that access a file. Each file (IdFile) is represented as a set of I/O phases and it can have a number of the I/O phases NPhase associated with it. Considering that I/O phases can have a different number of I/O processes. We define the number of I/O processes for a file as npIdF ile, which corresponds to the maximum number of I/O phase processes. We summarize the main concepts at file level in Table I.

|
|  |

| Identifier | Application |
| --- | --- |
| npapp | Number of processes that the application needs to execute. |
| NFiles | Number of files used by the application. |
| STapp | Capacity storage required by the application for the input files, temporal files and input/output |
|  | files. |
|  | File |
| IdFile | File Identifier. |
| FileSize | File Size. |
| AccesMode | This can be sequential, strided or random. |
| FileAccesType | It determines if the file is open as read only(R), write only (W) or write and read (W/R). |
| AccessType | np processes can access shared Files or 1 File per Process. |
| NPhase | Count of phases of the file. |
| npIdF ile | Maximum number of processes of all phases. |
|  | Phase |
| IdPh | Identifier of an I/O Phase. |
| IdFile | File identifier. |
| IdProcess | Identifier of Process. |
| npIdP h | Number of processes implied in the phase. |
| weight | Data volume to be transferred during the phase, which is expressed in bytes. |
| #iop | Number of I/O operations. |
| IOP | Data access operation type, which can be write, read, or write/read. |
| rs | Request size of operation that is data amount to be transferred by an I/O operation. |
| of fset | Operation offset, which is a position in the file’s logical view. |
| disp | Displacement into file, which is the difference between the offset of two consecutive I/O |
|  | operations. |
| dist | Distance between two I/O operations, which is the difference between subticks of two consecutive |
|  | I/O operations. |
| rep | Number of repetitions per phase. |

# *C. Concepts at Phase Level*

An I/O phase (PhIO) is a sequence of the I/O operations in the file's logical view. This considers the spatial access pattern, which shows how the processes access a file, as well as the temporal access pattern, which shows the order of occurrence of I/O events. The I/O phases are defined for each file opened by a parallel application, therefore a file is represented as a set of I/O phases. Figure 2 depicts the I/O phases for an access type 1 file per process.

We assign an identifier IdPh to each phase of a file IdFile. Furthermore, the identifiers IdProcess and count (npIdP h) of I/O processes are associated to each phase (See Table I).

To extract the temporal pattern, we define concepts tick and subtick. Tick is used to register the communication and I/O MPI events. Subtick is used to register POSIX-IO events. These concepts allow us to establish the logical order of MPI and POSIX events, as well as to identify the dependencies between the processes implied during the application execution and represent the general logical order of the application's I/O events. The tick and subtick make it

possible to have a system-independent model because we do not have dependencies with the system clock.

Figure 2 shows that an I/O phase is representing an I/O pattern. Phase 1 represents an I/O pattern (r,w) which is repeated three times. The pattern is the main characteristic to be considered to delimit an I/O phase. Besides, we can observe in Figure 2 that MPI events are also bounding the I/O phases identified. MPI events are represented by us with a tick, which is the second characteristic to delimit an I/O phase. However, for the subticks, it could present some cases where the I/O phase is limited by compute bursts and in such cases, we should use the count of instructions of the compute burst to decide if we are in the presence of a new I/O phase. This value must be defined depending on the impact of the data generated during a compute burst on the I/O system.

Two consecutive operations are similar whether: rs(IOPi)/rs(IOPi+1), disp(IOPi)

/disp(IOPi+1) and dist(IOPi)/dist(IOPi+1) and their value is between X and Y. Where X and Y are the values that allow us to define the rank to determine if two operations are similar. We define this rank between 0.8 and 1.2.

![](_page_3_Figure_0.png)

Figure 2. Representation of the I/O phases of a parallel application. The view corresponds to an I/O process for an access type 1 file per process. Tick and subtick are used to obtain the order of occurrence of the events of the application. An I/O phase is a consecutive sequence of similar I/O operations. Phase properties represent the data volume to be transferred during a phase and the I/O pattern.

Once the I/O phases are identified, we calculate the data to be transferred during an I/O phase denominated weight, which depends on npIdP h, rs and #iop and it is calculated by expression 1.

$$weight_{IdPh}=np_{IdPh}\times rs\times\#loop\times rep\tag{1}$$

The parallel application's files are represented based on their I/O phases which, seen as a whole, depict the I/O behavior model.

#### IV. VALIDATION OF THE I/O MODEL

In this section, we show the extraction of the I/O behavior model for MADspec's I/O kernel MADbench2 [10] and the real application ABySS [3]. These models can be used to replicate the I/O behavior of the MADbench2 benchmark and the ABySS application in different HPC systems. The I/O strategy of the selected applications is 1 file-per-process.

We work in different systems and filesystems because tracing at POSIX-IO layer requires validating that the model's concepts are independent of the I/O system. Model extraction is carried out in four HPC systems showed in Table II.

To extract the values of I/O concepts defined by the model, we select Darshan [11] and VampirTrace [12] tools. Darshan is an HPC I/O profiling tool that allows us to capture the application's I/O behavior, such as patterns of access at POSIX-IO, MPI-IO and HDF5 layer. This tool allows us to characterize the application I/O behavior of HPC applications and provides statistical information. We use Darshan to extract the information to define the spatial I/O pattern.

VampirTrace is a tracing tool for parallel applications. This allows us to observe the full behavior of the application. We use VampirTrace to extract the temporal I/O pattern.

MADbench2 [13] is a tool for testing the overall integrated performance of the I/O, communication and calculation subsystems of massively parallel architectures under the stress of a real scientific application. MADbench2 can be run in IO mode, in which all calculations/communications are replaced by busy-work. Running MADbench2 requires an n 2 number of processors. A detailed description of the different parameters is presented in [13].

We have focused our analysis on POSIX I/O mode. We extract the I/O behavior model of the MADbench2 by using IOMETHOD=POSIX, BWEX=1.0, RMOD=WMOD=1, FILETYPE=UNIQUE, NO BIN=8 and KPIX=25; and FBLOCKSIZE is adjusted to 8 MiB for GPFS at the LRZ's HPC systems and to 1 MiB for Lustre at the Finisterrae2.

We extracted the MADbench2's traces with the VampirTrace tool. Then, we have analyzed these traces and we have identified five I/O phases for each file of the parallel application. Table III presents I/O concepts at phase level.

In Figure 3, the graph on the left presents a total of 512 POSIX-IO operations that correspond to fwrite and fread, as well as showing the request size ( 298 MiB) for all operations, and as can be observed, these values are independent from the underlying I/O system.

Table IV details the concepts at application and file level. This reflects the values obtained for MADbench2 using different configurations. The same values are obtained in four HPC systems. Values from npapp = 25 are obtained in SuperMUC and CoolMUC2 systems. The results correspond to a different number of processes for 25KPIX and 90KPIX workloads.

MADBench2's I/O Phases are similar using a different number of MPI processes and workload. However, to define generic phases we need to consider the following equations for #iop: Phase 1: #iop = NO BIN, Phase 2: #iop = 2, Phase 3: #iop = NO BIN - 4, Phase 4: #iop = 2, Phase 5: #iop = NO BIN. Furthermore, the rs depends on NO PIX and npapp. To obtain other I/O concepts at phase level, we need to consider the values presented in Table IV. This presents different rs by using different NO PIX and npapp.

| Components |  | Capita | Finisterrae2 | SuperMUC | CoolMUC2 |
| --- | --- | --- | --- | --- | --- |
|  |  | (HPC4EAS) | (CESGA) | (LRZ) | (LRZ) |
| Compute Nodes |  | 13 | 306 | 9216 | 384 |
| CPU cores (per node) |  | 4 | 24 | 16 | 28 |
| RAM Memory |  | 16GB | 128GB | 32GB | 64GB |
| Local Filesystem |  | Linux ext3 | Linux ext4 | Linux ext3 | Linux ext3 |
| Global Filesystem (GFS) |  | NFS | NFS | NFS | NFS |
| Capacity of GFS |  | 46GB | 1.1TB | 10x564x10TB | 1000TB |
| Global Filesystem (PFS) |  | PVFS2 (2.8.7) | Lustre | GPFS | GPFS |
| Capacity of PFS |  | 175GB | 695TB | 12PB | 1.3PB |
| MPI-Library |  | mpich2 (1.5) | mpich2 (1.5) | IBM PE | Intel MPI |
| Number of data servers |  | 4 | 1 | 80 NSD | 4 NSD |
| Number of | Metadata | 1 | 1 |  |  |
| Server |  |  |  |  |  |
| Stripe Size |  | 64KiB | 1MiB | 8MiB | 8MiB |

![](_page_4_Figure_1.png)

![](_page_4_Figure_2.png)

![](_page_4_Figure_3.png)

![](_page_4_Figure_4.png)

We can observe that the MADBench's I/O behavior model is similar for different workloads and MPI processes and I/O phases represent the I/O pattern in a way that can be portable to other HPC I/O systems.

#### *A. Extracting the I/O Model: ABySS*

ABySS is a parallelized sequence assembler that is specialized in assembling large genomes from short sequences, using the pair-end (forward and reverse) method [3]. The ABySS algorithm proceeds in two phases.

ABYSS-P is an MPI version of the Bruijn graph assembler, which corresponds to the first phase.

We extract the I/O behavior model of ABYSS-P in the CoolMUC2, SuperMUC and Finisterrae2 HPC systems. We trace ABYSS-P using VampirTrace to identify the I/O phases and define the model. Figure 4 shows ABYSS-P for a small test by using 4 MPI processes, to assemble paired reads in two files named reads1.fastq and reads2.fastq into contigs in a file named test-bubbles.fa; and k=25.

This small case allows us to identify the temporal order of the I/O phases. An I/O phase for two input files can be observed at the beginning of the running and an I/O phase for two temporary files for each MPI process at the end.

In this case, for the application concepts, we have two input files and npapp ∗ 2 output files. If we execute the application using 128 process, we obtain 256 output files.

But independently of the number of processes, only processes 1 and 0 read from File1 and File 2 respectively, where the file size for each one is 17 GiB, access type is sequential and file access type is only read. The file size of the temporal files is less than 1 MiB in total. Concerning the phase concepts, we only focus on the input files because the temporary files are very small and they do not have any impact on the I/O system. We identify read and seek operations in the input files.

![](_page_5_Figure_0.png)

Figure 4. Vampir trace for ABYSS-P using 4 MPI processes. The dark green triangles correspond to the I/O events, the dark green triangles and red ones correspond to multiple I/O events, the yellow ones to the time of I/O operations, the green areas to the time of user operations and the red ones to the time for MPI events. Two I/O bursts can be observed, at the beginning, where processes 0 and 1 read from the File1 and File2 respectively. At the end, each MPI process writes into two temporary files (File3 i and File4 i). ABYSS-P accesses a total of 2 + np × 2 files.

| TABLE III |
| --- |
| MADBENCH2 PHASES USING 16 MPI PROCESSES, 25KPIX AND 8 |
| NO BIN. |

| Concepts | Phases for ∀ F ilei |  |  | with i ∈ (0..npapp | − 1) |
| --- | --- | --- | --- | --- | --- |
| IdPh | Ph1 | Ph2 | Ph3 | Ph4 | Ph5 |
| IdFile | F ilei | F ilei | F ilei | F ilei | F ilei |
| IdProcess | i | i | i | i | i |
| npIdP h | 1 | 1 | 1 | 1 | 1 |
| rep | 1 | 1 | 1 | 1 | 1 |
| #iop | 8 | 2 | 12 | 2 | 8 |
| IOP | w | r | (w,r) | w | r |
| rs |  |  | 312500000 |  |  |
| weight | 2.32GiB | 596MiB | 3.5GiB | 596MiB | 2.32GiB |
| offset |  |  | 312500000 |  |  |
| disp |  |  | 312500000 |  |  |

In Table V, it can be observed that the application executes 2135744 I/O operations (#iops) in each input file and in 8191 Bytes request size.

Independently of HPC System and filesystem, where ABYSS-P has been executed, we have the same values for the count of I/O operations (#iops) and the request size (rs) (See Figure 3, right graph). Table V shows the concept at phase level for the two input files. ABYSS-P has the same I/O phases for each input file and the values obtained are the same in the three HPC systems utilized. Therefore the I/O behavior model is portable to other systems.

# V. USE OF THE MODEL: ABYSS USE CASE

In this section, we present an example of using the model for evaluating the impact of the global file system on the performance of the ABYSS-P parallel application. This work is performed taking into account the requirement of a specific user who was considering incorporating a parallel file system in their HPC cluster. A detailed analysis about this case is presented in [14].

In this case, we work in Virtual HPC clusters to replicate the structure of the original HPC cluster and to deploy the I/O virtual subsystem. We use our own plugin for the StarCluster tool [15], which allows us to deploy the PVFS2 file system quickly and automatically. Due to the cost and time necessary, exploring a range of new alternatives is often prohibitive on a Cloud environment, so we select the cloud resources to evaluate the ABYSS-P's I/O behavior model obtained in Section IV. Table VI shows the characteristics of Virtual HPC Clusters utilized for the experiments.

Figure 5 presents the bandwidth for IOR customized for ABYSS-P's I/O model on NFS and PVFS2. As can be seen, NFS obtains a bandwidth of 117 MiB/sec, in contrast, PVFS2 obtains as maximum 48 MiB/sec for the three configurations evaluated.

A parallel file system, such as PVFS2, is not suitable for the ABYSS-P I/O pattern. The low performance of PVFS2 is related to the small request size of read operations and here there are only two read processes. Furthermore, the fact that two MPI processes read from input files and send read data to the rest of the processes is clearly an obstacle for ABYSS-P scalability.

### VI. CONCLUSIONS

HPC scientific applications perform parallel I/O and this can be achieved by using I/O libraries (serial or parallel). Therefore, knowing the I/O behavior of these latter applications will allow us to understand their impact on the I/O system.

We have proposed a model to represent the I/O behavior of parallel applications that use serial I/O libraries as part of a more holistic model for I/O of parallel applications. The

| TABLE IV MADBENCH2 - APPLICATION FEATURES - ACCESSTYPE = 1 FILE X PROCESS - ACCESSMODE = SEQUENTIAL - FILEACCESSTYPE = W/R - npIdF ile =1. VALUES FROM 64 PROCESSES ARE NOT OBTAINED IN THE CAPITA CLUSTER. |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Application Concepts |  |  | File Concepts |  | Phase Concepts |
| npapp | NFiles | STapp | FileSize | NPhase | rs |
| (GiB) |  |  | (Bytes) |  | (Bytes) |

|  |  | Application Concepts |  | File Concepts |  | Phase Concepts |
| --- | --- | --- | --- | --- | --- | --- |
|  | npapp | NFiles | STapp | FileSize | NPhase | rs |
|  |  |  | (GiB) | (Bytes) |  | (Bytes) |
| KP IX = 25 |  |  |  |  |  |  |
|  | 16 | 16 | 37.25 | 2500000000 | 5 | 2500000000 |
|  | 25 | 25 | 37.25 | 1600000000 | 5 | 1600000000 |
|  | 64 | 64 | 37.25 | 625000000 | 5 | 625000000 |
|  | 100 | 100 | 37.25 | 400000000 | 5 | 400000000 |
|  | 400 | 400 | 37.25 | 100000000 | 5 | 100000000 |
| KP IX = 90 |  |  |  |  |  |  |
|  | 256 | 256 | 965.60 | 4050000000 | 5 | 4050000000 |
|  | 400 | 400 | 965.60 | 2592000000 | 5 | 2592000000 |
|  | 576 | 576 | 965.60 | 1800000000 | 5 | 1800000000 |

TABLE VI DESCRIPTIVE CHARACTERISTICS OF THE VIRTUAL CLUSTERS (VCC) ON AMAZON EC2.

I/O components VCC 1 VCC 2 Instance c3.2xlarge c3.2xlarge Number of Instances 6 6 Temporal Storage Ephemeral Ephemeral Persistent Storage EBS EBS Temporal Device SSD SSD

192/3000)

100GB 64GB

- 400GB

- 1

SSD(GP 300/3000)

(2.8.8)

Persistent Device SSD(GP

Capacity of Persistent

Parallel Storage Capac-

Number of Metadata

Storage

ity

Server

|  | ABYSS PHASES FOR THE INPUT FILES. |  |
| --- | --- | --- |
| Concepts | Phases |  |
| IdPh | Ph1 | Ph1 |
| IdFile | File1 | File2 |
| IdProcess | 0 1 |  |
| npIdP h | 1 1 |  |
| #iop | 2135745 | 2135745 |
| IOP | r r |  |
| rs | 8191 | 8191 |
| rep | 1 1 |  |
| weight | 17GiB | 17GiB |
| offset | 8191 | 8191 |
| disp | 8191 | 8191 |

TABLE V

![](_page_6_Figure_4.png)

File system Local ext4 ext4 File system Global NFS PVFS2

Number of data servers - 5

![](_page_6_Figure_5.png)

Figure 5. Bandwidth obtained on VCC1 and VCC2 using IOR customized for the ABYSS-P's I/O model. The x-axis represents the different configurations for the file system, NFS and PVFS2 by using different number of DFs. To replicate the I/O concurrency into two input files, we run two concurrent instances of IOR benchmark. The IOR was executed in the same HPC system that ABySS and we was obtain the similar bandwith.

I/O behavior model is organized in phases, which allows us to replicate the application behavior in other HPC systems. As the applications use serial I/O libraries, the analysis has been carried out at the POSIX layer. We described the main concepts to define the I/O behavior model. These concepts are independent of the system because we have considered a portable model.

We have extracted the I/O models of the MADbench2 and ABYSS-P. These applications have been executed in four HPC systems with different file systems. The experiments validation showed that our I/O model is portable because it is not influenced by the software stack of the four HPC systems. The experimental results showed that the information extracted with the I/O model allows us to evaluate an I/O model with specific behaviour whose file system is more appropriate.

#### ACKNOWLEDGMENT

This research has been supported by the MINECO Spain under contract TIN2014-53172-P and partially supported by the CloudMas as Government Competency of AMAZON Web Services (AWS). The research position of the PhD student P. Gomez has been funded by a research collaboration agreement, with the "Fundacion Escuelas ´ Universitarias Gimbernat".

The authors thankfully acknowledge the resources provided by the Centre of Supercomputing of Galicia (CESGA, Spain) and the Leibniz Supercomputing Centre (LRZ, Germany).

#### REFERENCES

- [1] S. Mendez, D. Rexachs, and E. Luque, "Modeling Parallel Scientific Ap- ´ plications through their Input/Output Phases," in *CLUSTER Workshops*, vol. 12, 2012, pp. 7–15.
- [2] W. Loewe, T. MacLarty, and M. C, *IOR Benchmark*, 2012, accessed: 2016-05-14. [Online]. Available: https://github.com/chaos/ior/ blob/master/doc/USER\ GUIDE
- [3] J. T. Simpson, K. Wong, S. D. Jackman, J. E. Schein, S. J. Jones, and I. B. c¸, "ABySS: a parallel assembler for short read sequence data," *Genome research*, vol. 19, no. 6, pp. 1117–1123, 2009.
- [4] S. Byna, Y. Chen, X.-H. Sun, R. Thakur, and W. Gropp, "Parallel I/O Prefetching Using MPI File Caching and I/O Signatures," in *Proceedings of the 2008 ACM/IEEE Conference on Supercomputing*, ser. SC '08. Piscataway, NJ, USA: IEEE Press, 2008, pp. 44:1–44:12. [Online]. Available: http://dl.acm.org/citation.cfm?id=1413370.1413415
- [5] J. He, J. Bent, A. Torres, G. Grider, G. Gibson, C. Maltzahn, and X.- H. Sun, "I/O acceleration with pattern detection," in *Proceedings of the 22nd international symposium on High-Performance Parallel and Distributed Computing*. ACM, 2013, pp. 25–36.
- [6] M. Kluge, A. Knupfer, M. M ¨ uller, and W. E. Nagel, "Pattern Matching ¨ and I/O Replay for POSIX I/O in Parallel Programs," in *Proceedings of the 15th International Euro-Par Conference on Parallel Processing*, ser. Euro-Par '09. Berlin, Heidelberg: Springer-Verlag, 2009, pp. 45–56.
- [7] B. Behzad, H. V. T. Luu, J. Huchette, S. Byna, Prabhat, R. Aydt, Q. Koziol, and M. Snir, "Taming parallel I/O complexity with autotuning," in *2013 SC - International Conference for High Performance Computing, Networking, Storage and Analysis (SC)*, Nov 2013, pp. 1– 12.
- [8] B. Behzad, S. Byna, Prabhat, and M. Snir, "Pattern-driven Parallel I/O Tuning," in *Proceedings of the 10th Parallel Data Storage Workshop*, ser. PDSW '15. New York, NY, USA: ACM, 2015, pp. 43–48. [Online]. Available: http://doi.acm.org/10.1145/2834976.2834977
- [9] B. Behzad, S. Byna, S. M. Wild, A. Prabhat, and M. Snir, "Dynamic Model-driven Parallel I/O Performance Tuning," in *IEEE Cluster 2015*, IEEE. Chicago, IL: IEEE, 09/2015 2015.
- [10] J. Borrill, L. Oliker, J. Shalf, H. Shan, and A. Uselton, "HPC Global File System Performance Analysis Using a Scientific-application Derived Benchmark," *Parallel Comput.*, vol. 35, no. 6, pp. 358–373, Jun. 2009. [Online]. Available: http://dx.doi.org/10.1016/j.parco.2009.02.002
- [11] P. Carns, R. Latham, R. Ross, K. Iskra, S. Lang, and K. Riley, "24/7 Characterization of Petascale I/O Workloads," in *2009 IEEE International Conference on Cluster Computing and Workshops*. IEEE, 2009, pp. 1–10.
- [12] A. Knupfer, H. Brunst, J. Doleschal, M. Jurenz, M. Lieber, H. Mickler, ¨ M. S. Muller, and W. E. Nagel, "The vampir performance analysis tool- ¨ set," in *Tools for High Performance Computing*. Springer, 2008, pp. 139–155.
- [13] "MADbench2," https://crd.lbl.gov/departments/computational-science/ c3/c3-research/madbench2/, Accessed June 2016.
- [14] P. Gomez-Sanchez, D. Encinas, J. Panadero, A. Bezerra, S. Mendez, M. Naiouf, A. De Giusti, D. Rexachs, and E. Luque, "Using AWS EC2 as Test-Bed infrastructure in the I/O system configuration for HPC applications," *Journal of Computer Science & Technology '16*, vol. 16, no. 2, pp. 65–75, 2016.
- [15] "Starcluster by mit," http://http://star.mit.edu/, accessed: 2016-05-02.

