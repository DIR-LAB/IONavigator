# A Transparent Collective I/O Implementation

Yongen Yu, Jingjin Wu, Zhiling Lan Department of Computer Science Illinois Institute of Technology Chicago, USA {yyu22, jwu45, lan}@iit.edu

Nickolay Y. Gnedin Theoretical Astrophysics Group Fermi National Accelerator Laboratory Batavia, IL gnedin@fnal.gov

*Abstract***—I/O performance is vital for most HPC applications especially those that generate a vast amount of data with the growth of scale. Many studies have shown that scientific applications tend to issue small and noncontiguous accesses in an interleaving fashion, causing different processes to access overlapping regions. In such scenario, collective I/O is a widely used optimization technique. However, the use of collective I/O deployed in existing MPI implementations is not trivial and sometimes even impossible. Collective I/O is an optimization based on a single collective I/O access. If the data reside in different places (e.g. in different arrays), the application has to maintain a buffer to first combine these data and then perform I/O operations on the buffer rather than the original data pieces. The process is very tedious for application developers. Besides, collective I/O requires the creating of a file view to describe the noncontiguous access patterns and additional coding is needed. Moreover, for the applications with complex data access using dynamic data sizes, it is hard or even impossible to use the file view mechanism to describe the access pattern through derived data types. In this study, we develop a user-level library called transparent collective I/O (TCIO) for application developers to easily incorporate collective I/O optimization into their applications. Preliminary experiments by means of a synthetic benchmark and a real cosmology application demonstrate that the library can significantly reduce the programming efforts required for application developers. Moreover, TCIO delivers better performance at large scales as compared to the existing collective functionality provided by MPI-IO.** 

# *Keywords-component; Transparent Collective I/O, Collective I/O, Parallel I/O, MPI, One-sided communication, I/O intensive applications, HPC*

#### I. INTRODUCTION

Studies have shown that the processes of parallel applications tend to access a large number of small and noncontiguous pieces of data from a file, leading to the access of overlapping regions by different processes [1] [2] [3] [4]. Many applications need to map their multidimensional computing volume to one-dimensional file blocks in the

Douglas H. Rudd Research Computing Center University of Chicago Chicago, USA drudd@uchicago.edu

Andrey Kravtsov Department of Astronomy and Astrophysics The University of Chicago Chicago, IL andrey@oddjob.uchicago.edu

eventual file order before performing I/O. For example, Scalable Earthquake Simulation (SCEC) partitions the 3D computing volume into a set of slices and assigns each slice to a core [5]; both S3D and Pixie3D divide their computing volumes into small cubes and assign each small cube to one core [6]. If mapping all the cells of the computing volume oneby-one in the order of x, y, and z, each process would access many small noncontiguous data blocks in an interleaving fashion (see Figure 1). Such I/O access patterns lead to poor parallel I/O performance and optimizations are necessary. Collective I/O [7] is a common optimization mechanism that is used to improve parallel I/O performance with such access patterns. That is, collective I/O is used to improve IO performance when each process accesses several noncontiguous portions of a le and the requests of different processes are interleaved and together span large contiguous portions of the le [7].

![](_page_0_Figure_11.png)

Figure 1. An example to illustrate the mapping from multiple dimensional computing volume to one dimensional file blocks, where each slice of the computing volume is assigned to a process. For writes, each process outputs four noncontiguous blocks with the stride distance equal to eight cells.

Despite the compelling advantage of collective I/O, studies have shown that some applications prefer to use POSIX (or POSIX stream) rather than using collective functionality

provided by MPI-IO [8]. The existing collective functionality provided by MPI-IO (denoted as "the original collective I/O (OCIO)" in the rest of this paper) is not transparent to applications, and requires extra coding from application developers. We argue there are three issues with OCIO.

First, an application may use multiple in-memory data structures to store their data. Since OCIO is an optimization for a single collective I/O call, data blocks from multiple data structures must be first combined and cached into an application level buffer before issuing a single collective MPI-IO call [9] [10] [11]. Maintaining such a buffer within each process requires additional programming efforts. Further, a poorly designed buffer can lead to a waste of memory. Hence, the first question is: *can we let application developers focus on their I/O operations and free them from explicitly manipulating an extra application-level buffer to use collective I/O?*

Second, OCIO requires users to define a file view in their code to handle noncontiguous I/O accesses from multiple application processes. Each file view consists of two parts: the elementary data types to describe individual data elements and the file data types to describe data distribution in the file. Again, creating a file view requires extra coding. The second question is: *can we free application developers from writing extra file view code for using collective I/O?*

Finally, many parallel applications perform computations using complex, dynamic data structures that change during the course of execution. As a result, the noncontiguous data blocks are of different sizes. It is hard or even impossible for users to use a single derived data type instance to describe these data blocks. Hence the third question is: *can we use collective I/O to boost parallel I/O performance of the applications whose data blocks are of different sizes and varying distances?* 

To address the above problems, in this paper we design and develop a user-level library, called transparent collective I/O (TCIO), to facilitate the use of collective I/O for parallel applications with random noncontiguous access patterns. The library exposes POSIX-like interfaces for applications to perform parallel I/O operations. Application developers are freed from writing derived data types to describe the noncontiguous access patterns of their codes. The library is built on two key elements. First is a 2-level buffer approach. When an application calls the library, the library transparently creates two levels of buffers per application process. The level-1 buffers are responsible for combining small data blocks within each process, and the level-2 buffers rearrange the I/O requests from different processes in a file-offset order. Second is the use of one-sided communication for data exchange among processes.

TCIO is a new implementation of collective I/O, which differs from the existing implementation provided by MPI-IO (i.e. OCIO) at four key aspects. First, TCIO frees application developers from explicit management of application-level buffers for achieving collective I/O. Second, by using TCIO, application developers do not need to write extra codes to describe file view. Both features can be easily observed by comparing Program 2 and 3 listed in Section V. Consequently, the amount of programming efforts needed by TCIO is significantly less than that required by OCIO. Third, TCIO facilities the use of collective I/O for the applications using complex, dynamic data structures like the cosmology application presented in Section V. Finally, TCIO adopts several optimization techniques to improve I/O performance including one-sided communication for data exchange among processes and lazy-loading for read operations.

We evaluate the library by means of both a synthetic benchmark and a real cosmology application. The synthetic benchmark is used to extensively compare TCIO as against ROMIO (an implementation of OCIO) [12] in terms of both programming efforts and I/O performance. The cosmology application highlights the benefits of TCIO in the case where OCIO cannot be used. Together, these case studies demonstrate that TCIO library can significantly reduce programming efforts from application developers, while providing comparable or even better I/O performance as against OCIO.

The remainder of this paper is organized as follows. Section II discusses the related work. Section III introduces the background of collective I/O. We describe the design methodology of TCIO in Section IV. Experiments are listed in Section V. Finally, we draw the conclusions in Section VI.

#### II. RELATED WORK

Recognizing that some scientific applications access multiple files simultaneously for different array data, G. Memik et al. introduce Multicollective I/O (MCIO) to extend Collective I/O by taking the inter-file access patterns into consideration [13]. Their study shows that determining the optimal MCIO access pattern is an NP-complete problem. Therefore, they propose two heuristics (Greedy Heuristic and Maximal Matching Heuristic) to determine the MCIO access patterns.

Overlapping computation with communication is a widely used optimization to reduce the overhead associated with parallel I/O in the field of HPC. V. Venkatesan et al. present the challenges associated with developing non-blocking collective I/O operations [14]. They extend the libNBC library in conjunction with Open MPI's OMPIO framework to handle non-blocking collective I/O operations.

W. Yu et al. claim that the time spent in the global process synchronization dominates the actual IO time and point out that there exists a "collective wall" in the performance of collective I/O [15]. To address the issue, the authors introduce a novel technique called partitioned collective I/O (ParColl) to augment the collective I/O protocol with new mechanisms for file domain partitioning, I/O aggregator distribution and intermediate file views. By using ParColl, a group of processes and their corresponding files are divided into a collection of small groups and each group performs I/O aggregation in a disjointed manner.

In [16], J. Blas et al. propose an alternative implementation of collective I/O, namely view-based collective I/O. It improves the performance of collective I/O by reducing the cost of data scatter-gather operations, file metadata transfer, consecutive collective communication and synchronization operations.

There are several studies on the improvem I/O by exploring parallelism and physical loc al. propose a new collective I/O strategy, calle Collective I/O (LACIO) [17]. This new collec explores on the physical data layout of the pa instead of the logical file layout for performan Basically, LACIO incorporates the physical and information from parallel file systems w middleware. Requests from aggregators an partitions are rearranged in a fashion that m physical data layout on storage servers of system. ment of collective cality. Y. Chen et ed Layout Aware ctive I/O strategy arallel file system nce optimization. data distribution with parallel I/O nd file domain's matches with the the parallel file

By considering the pattern of file strippin I/O nodes in the parallel file system, Zhang new Collective I/O implementation, named re which rearranges requests from multiple p presumed on-disk data layout so as to turn accesses into sequential accesses. Resonant requests to an I/O node to be from the same coordinates the requests from multiple proce node in a preferred order. ng over multiple et al. designed a esonant I/O [18], processes by the n non-sequential I/O allows I/O agent process or esses to each I/O

Many modern parallel file systems consistency rules via locking mechanisms, process to exclusive access the requested file concurrent I/O requests on the shared file. Du serialization caused by locking, W. Liao et a file domain partition methods (i.e., partition lock boundaries, static-cyclic partitioning, a partitioning) for collective I/O optimization [19 maintain data which assign a region in case of ue to the potential al. develop three ning aligned with and group-cyclic 9].

Unlike the aforementioned studies that foc collective I/O from the performance perspect intended to provide a new collective I/O imp conducts collective I/O optimization transp leveraging knowledge from the application user-level TCIO library frees application writing I/O optimization code. It also allows with complex access patterns to use collective cus on improving tive, this work is plementation that parently without ns. The resulting developers from s the applications I/O.

Collective buffering is often used implementations to boost parallel I/O perfo scale. It selects a subset of nodes to comm servers for the purpose of reducing IO conte While collective buffering can optimize a sing TCIO is a new implementation of collective I/ contiguous requests of a file from multiple that in this study we do not enable collective experiments. d in MPI-IO ormance at large municate with IO ention [20] [21]. gle collective call, /O targeting nonprocesses. Note e buffering in the

#### III. BACKGROUND OF COLLECTIV VE I/O

In this section, we first briefly describe co then demonstrate how to use collective example. ollective I/O, and I/O through an

# A. *Basic Design*

MPI derived data types are a key feat specification. They provide an elegant and express noncontiguous, mixed types of data. O of the MPI specification, inherits this feature. process to use the MPI derived data type insta ture of the MPI efficient way to OCIO, as a subset . It requires each ances to describe the noncontiguous access patterns a by laying out a "view" of the file vi subroutine. and pass them to the library ia the "MPI_File_set_view"

OCIO divides the I/O operations and an I/O phase [7]. When an subroutines to output the data in OCIO calculates the file domain a via the minimum and maximum file domain is then divided into equal, each region is assigned to a tempora aggregator). The data from the ap shuffled among the computing proc offset and placed in the temporary aggregators then perform write c processes to output data to the file sy invokes MPI-IO read operations, th delegators to move the data from buffers and then distribute them to th s into a data exchange phase application invokes OCIO n application level buffers, accessed by the application e offsets. The aggregate file disjointed file regions, and ary buffer per process (a.k.a. pplication level buffers are cesses according to the file buffers of aggregators. The calls on behalf of all the ystem. When an application he aggregators serve as I/O m files to their temporary he target processes.

# B. *An Example*

In order to clearly describe necessitated by using OCIO, we in here. Consider an application that p on two in-memory arrays of type in At write, the application first interl types at the same array location, an single, shared file in a round-robin m the programming efforts ntroduce a simple example performs computation based nt and double, respectively. leaves variables of the two nd then places variables in a manner.

![](_page_2_Figure_13.png)

![](_page_2_Figure_14.png)

Figure 2 shows the write opera using OCIO. Here we assume that two and the array length is three. Ea has to copy and combine the data o into one application level buffe optimization for one single MPI-I/O only operate on one in-memory application, the buffer combines th ations of the application by the number of processes is ach application process first f the two in-memory arrays er, because OCIO is an O call and each MPI call can y data structure. In this he variables in round-robin fashion: The first position of the buffer holds of the int array; the second position records th the *double* array; the third and fourth slots elements of the int array and *double* array variables are combined in the application level the first element he first element of hold the second y; finally, all the l buffer.

After combining the data, each application file view to define the noncontiguous acce bottom of Figure 2 illustrates the file views d access regions of different processes. Each file three parameters: displacement, etype and example, "etype" is a contiguous derived data of two numbers: one integer number and one "filetype" is a vector with the stride equals processes times the size of etype; the displ process one and process two are 0 an respectively. All the information is passed to t library through the "MPI_File_set_view" funct process creates a ess patterns. The describing the I/O e view consists of filetype. In this a type consisting e double number; s the number of lacements of the nd sizeof(etype) the collective I/O tion.

When the application invokes the collective subroutine to output the data buffered in the buffer, the I/O operations are divided into tw data exchange phase, all the noncontiguous ordered by the logical file offsets to form one data block. After that, the block is evenly par parts. The first part is assigned to the first second part is assigned to the second process process only needs to issue one contiguous a three small accesses during the I/O phase regions accessed by different processes are disj e MPI-IO writing application level wo phases. In the data blocks are large contiguous rtitioned into two process, and the . Therefore, each access instead of e. Moreover, the joint.

#### IV. TRANSPARENT COLLECTIVE I/O D IMPLEMENTATION ESIGN AND

In this section, we present the design and im TCIO, which is capable of transparently b performance of parallel applications with accesses. mplementation of boosting the I/O h noncontiguous

# A. *Main Design*

Figure 3 depicts the layered architecture top layer, it exposes POSIX-like inter applications to interact with the library. B library provides two levels of buffers t operations. The level-1 buffers are for comb data blocks within the same process locally, buffers are used to reorganize I/O accesse processes. The level-1 buffers are private t while the level-2 buffers are shared among processes through MPI-2 one-sided communic of TCIO. At the rfaces for MPI Beneath that, the to expedite I/O ining in-memory , and the level-2 s from different to each process, g all application cation.

Since TCIO, similar to OCIO, is an optim IO, it uses basic MPI-IO routines to move d level-2 buffers and the file system. mization for MPIdata between the

TCIO exposes POSIX-like interface applications to perform IO operations based data. It is capable of performing collective across multiple I/O requests. The levelindispensible component to deliver such a fea buffer is used to combine data blocks of accesses within the same process locally. es for parallel on each piece of I/O optimization 1 buffer is an ature. The level-1 a sequential I/O

![](_page_3_Figure_9.png)

Figure 3. The archetecture of tra ansparent collective I/O

The level-2 buffers are used t among application processes so a performance. Since the library information from the application accessed by the application, it does size it should allocate for the leve level-2 buffer consists of multiple eq segments of different processes are in a round-robin fashion according t Figure 3). This design achieves goo the buffered data from different operations, the application has to remote MPI process that holds the segment id (IDsegment), and the displa the segment (DISPblock) of the desire can be calculated using the followin to coordinate I/O requests as to improve parallel I/O does not leverage any regarding the file domain not know in advance what l-2 buffers. In TCIO, each qual sized segments and the mapped to the file regions to the logical file offset (see od load balance in terms of processes. As for lookup know the rank id of the e required data (IDrank), the acement from the starting of ed data block. These values g equations:

$$\mathrm{ID}_{\mathrm{rank}}=\frac{\mathrm{OFFSET}}{\mathrm{SIZE}_{\mathrm{segment}}}\,\mathrm{\%}\mathrm{NUM}_{\mathrm{processes}}\tag{1}$$

$$\mathrm{ID}_{\mathrm{Segment}}={\frac{\mathrm{OFFSET}}{\mathrm{SIZE}_{\mathrm{Segment}}}}\ /\mathrm{NUM}_{\mathrm{processes}}\tag{2}$$

 

DISP${}_{\text{block}}$ = OFFSET % SIZE${}_{\text{segment}}$ (3)

where *OFFSET* is the logical file of *SIZEsegment* is the size of one lev *NUMprocesses* is the number of proces library can calculate these three val logical file offset of a data block. ffset of the target data block, vel-2 buffer segment and ses of MPI application. The lues in O (1) time given the

The level-2 segment size (SIZEs for TCIO. If the segment size granularity of the underlying file sy compete with each other for the p region, leading to poor performan might render an extremely unbalanc MPI processes. Based on these facts stripe size (the locking granularity) o segment) is a crucial parameter is smaller than the lock ystem, MPI processes might rivilege to access a locked nce. A large segment size ced data distribution among s, we set segment size as the of underlying file system.

TCIO uses the level-1 buffers to combine multiple pieces of data together. The combined data are placed in the level-2 buffers as segments. If a combined data block were larger than the size of one level-2 buffer segment, it has to be subdivided and placed in different segments of the level-2 buffers. Since there is no benefit to setting the size of level-1 buffer larger than the segment size of the level-2 buffer, we set them to be equal, and each level-1 buffer is aligned with one level-2 buffer segment.

For write operations, TCIO buffers the data blocks in the level-1 buffer. It also retains the -./012345 together with the length of the data blocks. Processes individually send out level-1 buffered data to the level-2 buffer when either the file domain of cached data blocks exceeds the size of the level-1 buffer or the application explicitly invokes the "flush" function. During the reading phase, TCIO moves the data in the other direction. Instead of using a preloading technique, TCIO uses a lazyloading strategy for read operations. In particular, when the application issues read calls, rather than loading the data, the library stores the address, the length and the -./012345 of the target data blocks. The real data-loading tasks take place when either the file domain of cached reads exceeds the size of the level-1 buffer, or the applications explicitly request the library to load data.

OCIO uses non-blocking communication to shuffle data across the computing processes at the data exchange phase in the all-to-all manner. Non-blocking communication (Isend/Irecv) is a two-sided communication model, which requires a matching pair on both sender and receiver sides. OCIO first issues MPI_Irecv to receive data from all processes, then issues MPI_Isend to send data to all processes, and then waits until all communication complete [22]. TCIO, however, cannot use two-sided communication. It allows processes to issue I/O calls for each piece of data individually, and as a result, different processes may issue a different number of I/O requests. TCIO instead relies on one-sided communication, which removes the requirement of a matching pair in both sender and receiver sides and allows the processes to initiate an end-to-end data movement across computing nodes from either the sender or receiver side. During writes, TCIO initiates data movements from the sender side. During reads, the receivers pull over the data from the level-2 buffer of the remote process.

In one-sided communication, "MPI_Win_fence" is the simplest approach to allow all processes to synchronize. However, "MPI_Win_fence" is a collective call, which by nature would break the TCIO design, which allows all the I/O accesses to be performed independently. Therefore, we use the lock-request paradigm ("MPI_Win_lock" and "MPI_Win_unlock") in the TCIO implementation.

When TCIO moves data between level-1 and level-2 buffers, these data consist of multiple disjointed data blocks. If it were to move each piece of data with its own one-sided communication call (MPI_Get, MPI_Put), this would cause a large number of network connections, which would in turn degrade the performance. We use "MPI_Type_indexed" to combine multiple data blocks as one derived data type instance. The library can then transfer the newly created data type instance by a single one-sided communication call.

# B. *Implementation*

TCIO library is written in C language. It consists of about a thousand lines of code. We distribute it as a user-level library. Program 1 is the API definition of the library. It exposes POSIX-like I/O interfaces for parallel applications. It also allows applications to perform I/O operations based on MPI data types. "tcio_flush" function allows the application to explicitly move data from the level-1 buffers to the level-2 buffers. It is a collective call, which invokes "MPI_Barrier" to synchronize among processes. Since the library uses a lazyloading strategy for reading operations, the actual data are not loaded into the target places after the read calls return. The library provides "tcio_fetch" function to enable applications to inform the library to load the desired data blocks to the target locations explicitly. "tcio_close" function issues "MPI_barrier" to synchronize among processes before outputting data from the level-2 buffers to file system.

# **Program 1:** API Definition

tcio_file * tcio_open(char * fname, int mode)

tcio_write (tcio_file *fh , void * data, int count, MPI_Datatype type)

tcio_write_at (tcio_file *fh , MPI_Offset offset,void * data, int count, MPI_Datatype type)

tcio_read(tcio_file * fh, void * data, int count, MPI_Datatype type)

tcio_read_at(tcio_file * fh, MPI_Offset offset , void * data, int count, MPI_Datatype type)

tcio_seek(tcio_file * fh, MPI_Offset offset, int whence)

tcio_flush(tcio_file * fh)

tcio_fetch(tcho_file * fh)

tcio_close(tcho_file * fh)

To use TCIO, a user needs to specify the segment size and the number of segments per process.

# C. *An Example*

Figure 4 uses the same example as shown in Figure 2 to demonstrate the algorithm of TCIO. For simplicity, we assume that each process holds one segment of the level-2 buffer.

At the first step, process 1 outputs the first element of the int array via a TCIO call. Since this piece of data will be stored at the beginning of the file, process 1 aligns its level-1 buffer with the first segment of the level-2 buffer and places the int value at the beginning of the level-1 buffer. After that, process 1 issues another TCIO call to output the first element of the *double* array, which is also stored in the level-1 buffer. Similarly, process 2 aligns its level-1 buffer with the first segment of the level-2 buffer and places the first element of the two in-memory arrays in its level-1 buffer.

![](_page_5_Figure_0.png)

Figure 4. The work flow of TCIO. Step 1 shows the con 3 presents the contents of level-1 and level-2 buffers aft level-2 buffers after the application outputs the third elem ntents of the level-1 and level-2 buffers after the application outputs the ter the application outputs the second elements of each array. Step 5 sho ments of each array. In step 6,the application outputs all the data in the l Finally, all the data are transferred to a file. first elements of each array. Step ws the content of the level-1 and level-1 buffers to level-2 buffers.

At the second step, process 1 outputs the s the two in-memory arrays by invoking anothe Since these two pieces of data fall into the sam level-2 buffer with the previous writes, they the current level-1 buffer. At this stage, proce the second elements of its two in-memory arr buffer because these data blocks fall into a diff the level-2 buffer. It must first flush the da buffer to the global level-2 buffer. econd element of er two write calls. me segment of the can be placed in ss 2 cannot place rays in its level-1 fferent segment of ata in its level-1

#### At the third step, process 2 aligns its levelsecond segment of the level-2 buffer and p elements of the two in-memory arrays in level--1 buffer with the laces the second -1 buffer.

At the fourth step, process 1 attempts to pair of elements. Since these writes fall o segment that the level-1 buffer is aligned w flushes the level-1 buffer and moves these d level-2 buffer. output the third outside the first with, the library ata blocks to the

At the fifth step, process 1 aligns the levelsecond segment of the level-2 buffer and elements of the two arrays in the level-1 buffe places the third elements of its two in-mem level-1 buffer. -1 buffer with the places the third er. Process 2 also mory arrays in its

#### At the sixth step, both the processes flush data from the level-1 buffers to the level-2 buff h all the buffered ffers.

By comparing Figure 4 and Figure 2, it actual I/O operations adopted by TCIO and OC As we will show in the next section, programming efforts needed by TCIO is signi that required by OCIO. Further, TCIO offer better I/O performance as against OCIO. is clear that the CIO are different. the amount of ificantly less than rs comparable or

#### V. EXPERI IMENT

# A. *Testbed*

We evaluate TCIO library on machine at TACC [23]. Lonestar i each node features two 6-Core installed on the computing nod connected by Mellanox InfiniBan topology with a 40Gbit/sec point node holds up to 24GB memory Lustre [24] is installed on this mach storage capability. Lonestar is c storage targets (OST). The stripe siz file is stored on a single OST. We u following experiments. SGE is used n the production Lonestar is a 1,888-node cluster and processors. Centos 5.5 is des and these nodes are nd network in a fat-tree t-to-point bandwidth. Each . The parallel file system hine and provides up to 1PB onfigured with 30 object ze is 1MB. By default, each use the default setting in the d to provide batch services.

We evaluate the library by mean and a real parallel application. We OCIO with regard to programming e by using the benchmark. The appl the case where OCIO cannot be use to boost application I/O performan were conducted during the produc applications coexist in the system. T performance results, a minimum of for each experiment, and we present ns of a synthetic benchmark e compare TCIO as against efforts and I/O performance lication is used to illustrate ed, while TCIO can be used nce. All these experiments ction mode, meaning other To minimize the noise in the f three runs were conducted t the average values.

# B. *Synthetic Benchmark*

We create a benchmark to simu example application as shown in Fi the special pattern --- small no accessed by parallel processes in where collective I/O can optimize vanilla MPI-IO. As mentioned ear benchmark experiments is to compa IO performance by using TCIO and in the rest of this subsection, we l ulate the I/O accesses of the gure 2. The benchmark has oncontiguous data blocks an interleaving fashion --- I/O performance over the rlier, the main goal of our are programming efforts and OCIO respectively. Hence, list the results achieved by TCIO and OCIO. Before presenting the experimental results, we list the configuration parameters of the benchmark in Table I. The following configuration parameters are used:

$$\mathrm{NUM}_{\mathrm{array}}=2$$

TYPEarray =i, d

$$\mathrm{LEN}_{\mathrm{any}}=3$$

$$\mathrm{SIZE_{access}}=1$$

TABLE I. CONFIGURATION PARAMETERS

| Symbol | Description |
| --- | --- |
| method | 0: OCIO; 1: TCIO; 2 MPI-IO |
| NUMarray | The number of arrays within each process |
| TYPEarray | The data types of arrays separated by a comma. c: char; s: |
|  | short; i: integer; f: float; d: double |
|  | e.g. “i,d” means the first array is of integer type and the |
|  | second array is of double type |
| LENarray | The length of arrays |
| SIZEaccess | The number of array elements per I/O access. We can use it |
|  | to adjust the I/O access size. For example, if SIZEaccess |
|  | equals 4, the benchmark access four array elements for each |
|  | I/O call. |

# 1) *Programming Efforts*

Freeing application developers from writing extra code is a key motivation of this work. Before comparing TCIO and OCIO implementations on performance, we list their respective codes. Program 2 is the OCIO code and Program 3 is the TCIO code.

Program 2 shows the implementation by using OCIO library. First, each benchmark process has to create an application level buffer to combine data, and then appends segments of each array to the buffers in a round-robin fashion through two for loops. Finally, all the array values are combined within a single application level buffer. After that, each benchmark process creates two derived data types to describe the noncontiguous access patterns and passes such information to library by setting out the view of the file. A single collective write call is issued to output all the data in the buffer. At last, release the occupied memory space for further use. For simplicity, we just describe the buffer operations with a single sentence in Program 2. In practice, however, creating and maintaining these application level buffers requires significant programming efforts by the application developers.

Program 3 presents the code of the implementation using TCIO. Each benchmark process only needs to output the elements of each array through two for loops in POSIX I/O fashion. It first calculates the file offset of the data block, then seeks the file handle to that position and then places the data block there. Application developers do not have to manipulate application level buffers, create derived data types or set out file views. Applications can benefit from collective I/O optimization by using fewer lines of code in a simpler way.

# **Program 2:** Programming efforts by using OCIO

|
|  |

- 2. //Combine data in the buffer by two for loops for each i ∈ [1,LENarray] increase SIZEaccess
 for each j ∈[1, NUMarray] append the [ith ~ i+SIZEaccess) elements of array j to the end of the buffer

- 3. //Open file MPI_File_open(MPI_COMM_WORLD, file_name, mode, MPI_INFO_NULL, &handle)
- 4. //Set out file view
- block_size (sizeof(int)+sizeof(double))* SIZEaccess 5. disp my_rank *block_size
- 6. MPI_Type_contiguous (block_size, MPI_BYTE, &eType)
- 7. MPI_Type_commit(&eType)
- 8. MPI_Type_vector( LENarray/ SIZEarray, 1 , num_procs , eType, &fileType)
- 9. MPI_Type_commit(&fileType)
- 10. MPI_File_set_view(handle, disp, eType, fileType, "native", MPI_INFO_NULL)
- 11. MPI_File_write_all(handle, <address of the buffer>, LENarray/SIZEaccess*block_size, MPI_BYTE, &status)
- 12. MPI_File_close(&handle)
- 13. Release the buffer.

# **Program 3:** Programming efforts by using TCIO

- 1. block_size (sizeof(int)+sizeof(double))*SIZEaccess
- 2. handle tcio_open(file_name, mode)
- 3. for each i ∈ [1,LENarray] increase SIZEaccess a. pos my_rank*block_size
- +i*block_size*num_procs
- b. for each j ∈[1, NUMarray] i. tcio_write_at(handle,pos,arrayj[i], SIZEaccess, MPI_BYTE)
- ii. pos pos +<type size of array i> * SIZEaccess
- 4. tcio_close(handle)

# 2) *I/O Performance*

# a) *Impact of the Number of Processes*

In this subsection, we evaluate the performance of TCIO against OCIO with different numbers of processes. Table II shows the configurations of the benchmark. We vary the number of processes from 64 to 1024. Each process holds two in-memory arrays of integer and double types, respectively. The length of each local array is 4M.

![](_page_7_Figure_0.png)

Figure 5. I/O throughput of the synthetic benchmark with varying access sizes

TABLE II. EXPERIMENT CONFIGURATION

|  | Parameters |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
|  | NUMarray | TYPEarray | LENarray | SIZEaccess | NUMproc |
| Value | 2 | i,d | 4M | 1 | 64~1024 |

The left subfigure of Figure 5 shows the write throughput as a function of the number of processes. Collective I/O improves parallel I/O performance by aggregating large numbers of small and noncontiguous accesses into large fewer ones. Hence, the improvement of collective I/O for large I/O accesses is not evident. In this set of experiments, we set the access size to 1. From this figure, we observe that OCIO delivers better performance at small scales (<=256). TCIO, however, outperforms OCIO at large scale. OCIO exchanges data among computing nodes in all-to-all fashion. Each process receives data from all processes and then broadcast data to all processes through non-blocking I/O. The number of network connections increases quickly with the growth of computing nodes. TCIO uses one-sided communication to transfer data in end-to-end fashion. Each process sends or receives data from a single process each time. Thus the number of connections increases slower than that of OCIO. Moreover, OCIO performs all the communication at the same time, which might cause heavy traffic bursting in the network. TCIO, however, performs each communication individually. Therefore, TCIO achieves better writing performance as against OCIO at large scales (>=512).

The right subfigure of Fig. 5 presents the read throughput for the same set of experiments. In this figure, we can see that TCIO is better than OCIO. Moreover, we can observe that the gap between TCIO and OCIO is widened with the growth of compute nodes.

# b) *Impact of File Size*

In this set of experiments, we evaluate TCIO as against OCIO with different file sizes. We use the same configuration parameters listed in Table II except that we fix the number of processes at 64 and vary the LENarray from 1M to 64M, leading to the file size varies from 768MB to 48GB.

Figure 6 shows the write throughput of the benchmark with different dataset sizes. The key observation of this figure is that when the size of dataset is 48GB, the benchmark with OCIO fails to work. If the size of the entire dataset is 48GB and the number of process is 64, each process has to hold up to 0.75GB of data. By using OCIO, these data are first combined and cached in the application level buffers and then copied to the temporary buffers of the library. Therefore, each process has to provide 1.5GB (0.75*2) memory space for I/O operations. On Lonestar, the memory space is not sufficient for the benchmark to perform I/O operations with the code listed in Program 2. In TCIO, the benchmark does not have to combine all the data together in order to output them with a single call. Each process just has one reusable level-1 buffer and the size of which equals one segment size of the level-2 buffer. The size of the level-2 buffer equals the size of the temporary buffer in OCIO. Therefore, only 0.751GB(0.75GB+1MB) memory space is requires. TCIO outperforms OCIO in terms of memory utilization.

![](_page_7_Figure_9.png)

Fig. 7 shows the experimental results of read throughput for the same set of experiments. As for reads, TCIO delivers better performance than OCIO. Also, the benchmark fails to work with the code listed in Program 2 when the size of dataset is 48GB.

![](_page_8_Figure_0.png)

# 3) *Summary of Benchmark Results*

Table III summarizes the differences bet TCIO. OCIO requires applications to create an of buffers while TCIO does not. OCIO u mechanism, whereas TCIO exposes POSIX-li applications to perform I/O operations in a tra The number of lines of code for I/O operation is more than that of TCIO. In OCIO, the application level buffers from different proc large enough to hold all the output data, whil corresponding buffers in TCIO, the level-1 bu segment size of the level-2 buffers. The mem TCIO is more efficient than that of OCIO. Res view mechanism, OCIO is suitable for those easy-to-describe access patterns, while TCI library that can be used by a broad ra applications. tween OCIO and n additional level uses a file view ike interfaces for ansparent manner. ns by using OCIO total size of the cesses should be le the size of the uffers, equals one mory utilization of stricted by the file applications with IO is a generic ange of parallel

TABLE III. COMPARISION BETWEEN OCIO AND TCIO

|  | Table Column He |  |  | ead |
| --- | --- | --- | --- | --- |
|  | Original collective I/O |  |  | Transpa arent collective I/O |
| Application-level buffer | Yes |  |  | No |
| File view | Yes |  |  | No |
| Lines of code | Many |  |  | Few |
| Memory efficency | Poor |  |  | High |
| Restriction | access patterns that can | be | easily | Any PO OSIX-like access patterns |
|  | described by MPI |  |  |  |
|  | derived data types |  |  |  |

# C. *Cosmology Application*

In this subsection, we evaluate TCIO by cosmology simulation code called ART (Adap Tree) [25]. ART is a cell-based AMR ap divides the whole 3D space computing volu cells, so-called root cells. Each root cell computing unit. If higher spatial resolution is cell can be refined into eight finer cells. The f further refined and are organized in an octal t fully threaded tree (FTT) [26] to represent refi their relationship. The structures of thes means of a real ptive Refinement pplication, which ume into uniform is an individual s required, a root finer cells can be tree. ART uses a inement cells and se trees change dynamically throughout the course causes these trees to have different s of the computation, which structures and sizes.

In order to write the data into a f 3D computing volume to one-dim When the mapping is done by alloc of x, y, and z, each process would computing volume into multiple segments on disk in an interleavin patterns can benefit from the use of file, ART also must map the mensional on-disk blocks. cating the cells in the order d divide its cells within its segments and place these g fashion. Such I/O access collective I/O optimization.

Figure 8 shows the data layout described file data format [27]. Bo tree structure information are recor holds two variables, the depth of numbers of nodes of each level are will consist of 129 arrays of differ these arrays are adjacent in the f combine these arrays together. OC to explicitly manage the buffer. T performs the aggregation implicitly t of one FTT. It is a selfoth the variable values and rded in the file. If one FTT the tree equals 6, and the e {1,2,4,8,16,32}, one FTT rent types and sizes. Since file, a buffer is needed to IO requires the application TCIO, on the other head, through its level-1 buffer.

Since these FTT differ in the nu they represent different amount Processes will contain various num maintain a reasonable load balance. the lengths of the segments assign the normal distribution and use th generate 1024 random numbers to these segments. These segments a processes in a round-robin fashion. umber of cells they contain, of computational work. mbers of FTT in order to In our tests, we assume that ed to each process follows he following parameters to o represent the lengths of are in turn assigned to the

|  | TABLE IV. SEGMENT | TS GENERATION |  |  |
| --- | --- | --- | --- | --- |
|  | Param | meters |  |  |
|  | Distribution Mu |  | Sigma | Seed |
| Value | Normal 2048 |  | 128 | 5 |

![](_page_8_Figure_12.png)

![](_page_8_Figure_13.png)

Figure 8. Data layout t of one FTT

# a) *Programming Efforts*

In order to use OCIO, ART firs the file. Since the lengths of these st has to set out the view of segments are different, the application cannot use a single elementary data type to describe the data block of each segment. Moreover, FTT is a complex data structure, which is represented by many small arrays of different sizes and types. Even we can use derived data types (e.g. MPI_Type_create_struct) to describe the structure of the FTT, we still have to create an application level buffer to combine these arrays together. Manipulating an application level buffer to combine and buffer these data is also an arduous work, not to mention that these FTT instances are of different sizes, and we have to create different derived data type instances for different FTT. In short, it is hard to use OCIO for the application, at least with the similar programming efforts by using TCIO.

As for TCIO, ART code does not have to inform the library of the noncontiguous access pattern of the application via file view by using derived data types. Also, the application does not have to create application level buffers to combine data blocks. The only thing that the application needs to do is to output each piece of data individually and TCIO will handle collective I/O operations transparently to the application.

#### b) *I/O Performance*

In this set of experiments, we evaluate the parallel I/O performance of the ART code with TCIO as against vanilla MPI-IO. Both allow applications to perform I/O operations based on each piece of data individually except that the former incorporates collective I/O optimization. In the experiments, we let the simulation first dump the intermediate data and then restart from this snapshot.

Figure 9 and 10 show the write and read throughputs of the ART code by using TCIO as against vanilla MPI-IO with a variety of scales. It is evident that TCIO is much better, up to 100X faster than the vanilla MPI-IO. When the number of processes is equal to or larger than 512, ART with vanilla MPI-IO takes more than 90 minutes to complete. That is why the figures only present TCIO data when the number of processes is equal or larger than 512.

![](_page_9_Figure_5.png)

Figure 9. Write throughout of ART code

Another observation is that both the write and read throughputs of TCIO first increase with the increasing number of processes and then drop slightly. In this set of experiments, we test strong-scaling, meaning that the total number of root cells is fixed and the size of entire dataset is the same. When the computing scale is small, the aggregate I/O throughputs of compute nodes are the performance bottleneck. With the increasing number of processes, there will be more compute nodes to perform I/O operations. Hence, both the write and read throughputs grow with the increasing number of processes. On Lonestar, the centralized parallel file system Lustre is used to manage data. The number of I/O servers determines the bandwidth of the file system. If data-outputting rate overwhelms the bandwidth of the file system, application I/O throughputs stop increasing. Even worse, the competition among computing nodes will bring down the I/O performance. Therefore, the I/O throughputs of TCIO stop increasing and drop with the increasing of processes. Such a phenomenon indicates that the I/O performance of parallel large-scale applications subjects to the bandwidth of the underlying centralized parallel file system.

![](_page_9_Figure_9.png)

![](_page_9_Figure_10.png)

Figure 11. Read throughput of ART code

# D. *Experiment Summary*

In summary, our experimental results with the synthetic benchmark and the cosmology application indicate that:

- TCIO can greatly reduce user's programming efforts for using collective I/O in their applications (see Program 2 and Program 3). Moreover, the applications with complex dynamic access patterns like ART can benefit from collective I/O by using TCIO.
- Experimental results indicate that TCIO outperforms OCIO at large scales. A key reason is that TCIO utilizes one-sided communication for data exchange among processes, which can significantly reduce the network traffic. This is essential for those large-scale applications where the network bandwidth is the performance bottleneck.
- TCIO uses less memory than OCIO, thereby being appropriate for those memory-intensive applications.

#### VI. CONCLUSION

Collective I/O is a powerful technique for parallel applications to improve I/O performance in the case that applications perform small, noncontiguous I/O accesses in an interleaving fashion. Existing collective I/O implementations require application developers to explicitly describe the noncontiguous access patterns through derived data types and inform the library by setting out the file view. In the case of the application having multiple data structures, each application process must first combine all the data from different places into a single application level buffer in order to perform I/O operations by issuing a single call. All these require significant programming efforts from application developers. In addition, due to the limitation of derived data types, some applications with complex dynamic access patterns may not be able to use the existing collective I/O implementation.

In this paper, we have presented a user-level library, namely TCIO to address the issues described above. TCIO exposes POSIX-like interfaces for parallel applications to conduct collective I/O optimization. Our case studies have shown that the library can significantly reduce user's programming efforts. Moreover, it delivers better throughput as against the OCIO at large scales.

#### ACKNOWLEDGMENT

This work is supported in part by National Science Foundation grants OCI-0904670. This work used the Extreme Science and Engineering Discovery Environment (XSEDE), which is supported by National Science Foundation grant number OCI-1053575.

#### REFERENCES

- [1] P. Crandall, R. Aydt, A. Chien and D. Reed, "Input-Ouput Characteristics of Scalable Parallel Applications," in *Proceedings of Supercomputing '95*, 1995.
- [2] N. Nieuwejaar, D. Kotz, A. Purakayastha, C. Ellis and M.Best, "File-Access Characteristics of Parallel Scientific Workloads," *IEEE Transactions on Parallel and Distributed Systems*, vol. 7, pp. 1075-1089, October 1996.
- [3] E. Smirni, R, Aydt, A. Chien and D. Reed, "I/O Requirements of Scientific Applications: An Evolutionary View," in *Proceedings of the Fifth IEEE International Symposium on High Performance Distributed Computing*, 1996, pp. 49-59.
- [4] J. Lofstead, M. Polte, G. Gibson, S.A. Klasky, K. Schwan, R. Oldfield, M. Wolf and Q. Liu, "Six Degrees of Scientific Data: Reading Patterns for Extreme Scale Science IO," in *Proceedings of the 20th international ACM symposium on High-Performance Parallel and Distributed Computing*, San Jose, CA, June, 2011.
- [5] Y. Cui, K.B. Olsen, T.H. Jordan, K. Lee, J. Zhou, P. Small, D. Roten, G. Ely, D.K. Panda, A. Chourasia, J. Levesque, S.M. Day and P. Maechling, "Scalable Earthquake Simulation on Petascale Supercomputers," in *Proceedings of SC '10*, New Orleans, Louisiana, USA, 2010.
- [6] R. Sankaran, E. Hawkes, J. Chen, T. Lu, and C. Law, "Direct Numerical Simulations of Turbulent Lean Premixed Combustion," *Journal of Physics: conference series*, vol. 46, pp. 38–42, 2006.
- [7] R.Thakur, W.Gropp and E.Lusk, "Data Sieving and Collective I/O in ROMIO," in *Proc. of the 7th Symposium on the Frontiers of Massively parallel Computation*, 1999, pp. 182-189.
- [8] P. Carns, K. Harms, W. Allcock, C. Bacon, S. Lang, R. Latham and R. Ross, "Understanding and improving computational science storage access through continuous characterization," *Mass Storage Systems and Technologies, IEEE / NASA Goddard Conference on*, vol. 0, pp. 1-14, 2011.
- [9] M. Zingale. FLASH I/O Benchmark Routine -- Parallel HDF 5. [Online]. http://www.ucolick.org/~zingale/flash_benchmark_io/

- [10] W. Loewe, R. Klundt. IOR HPC Benchmark. [Online]. http://sourceforge.net/projects/ior-sio/
- [11] The Los Alamos National Lab MPI-IO Test. [Online]. http://public.lanl.gov/jnunez/benchmarks/mpiiotest.htm
- [12] ROMIO: A High-Performance, Portable MPI-IO Implementation. [Online]. http://www.mcs.anl.gov/research/projects/romio/
- [13] G. Memik, M. T. Kandemir, W. Liao, and A. Choudhary, "Multicollective I/O: A technique for exploiting inter-file access patterns," *Trans. Storage*, pp. 349-369, Aug. 2006.
- [14] V. Venkatesan, M. Chaarawi, E. Gabriel, and T. Hoefler, "Design and Evaluation of Nonblocking Collective I/O Operations," in *Recent Advances in the Message Passing Inerface (EuroMPI'10)*, vol. 6960, Santorini, Greece, 2011, pp. 90-98.
- [15] W. Yu, J. Vetter, "ParColl: Partitioned Collective I/O on the Cray XT," in *ICPP '08*, Portland, OR, 2008, pp. 562-569.
- [16] J. Blas, F. Isail, D. Singh, and J. Carretero, "View-based collective I/O for MPI-IO," in *Cluster Computing and the Grid, 2008. CCGRID '08*, 2008, pp. 409-416.
- [17] Y. Chen, X. Sun, R. Thakur, P. Roth, W. Gropp, "LACIO: A New Collective I/O strategy for Parallel I/O Systems," in *the 25th IEEE Int'l Parallel and Distributed Processing Sympsium(IPDPS2011)*, 2011.
- [18] X. Zhang, S. Jiang, and D. Kei, "Making Resonance a Common Case: A High-Performance Implementation of Collective I/O on Parallel FIle Systems," in *Parallel & Distributed Processing IPDPS '09*, 2009, pp. 1- 12.
- [19] W. Liao, and A. Choudhary, "Dynamically Adapting File Domain Partitioning Methods for Collective I/O Based on Underlying Parallel File System Locking Protocolssed ," in *High Performance Computing, Networking, Storage and Analysis, SC '08*, Austin, TX, 2008.
- [20] CRAY. [Online]. https://fs.hlrs.de/projects/craydoc/docs/books/S-2490- 40/html-S-2490-40/chapter-g1s9a5n5-oswald-benchmarkresults.html
- [21] NERSC. [Online]. http://www.nersc.gov/users/data-andnetworking/optimizing-io-performance-for-lustre/
- [22] K. Coloma, A, Ching, A. Choudhary, W.Liao, R. Ross, R. Thakur and L.Ward, "A New Flexible MPI Collective I/O Implemenation," in n *Proceedings of the IEEE Conference on Cluster Computing (Cluster 2006)* , Barcelona, Spain.
- [23] Extreme Science and Engineering Discovery Environment. [Online]. https://www.xsede.org/
- [24] Oracle. Lustre File System. [Online]. http://wiki.lustre.org
- [25] A. V. Kravtsov, A. A. Klypin and A. M. Khokhlov, "Adaptive Refinement Tree: A new High-resolution N-body code for Cosmological Simulations," in *Astrophyc. J. Suppl*, 1997, pp. 73-94.
- [26] A. M. Khokhlov, "Fully Threaded Tree Algorithms for Adaptive Refinement Fluid Dynamics Simulations," *Journal of Computational Physics*, 1998.
- [27] Y. Yu, D.H. Rudd, Z. lan, N.Y. Gnedin, A. Kravtsov and J. Wu, , "Improving Parallel IO Performance of Cell-based AMR Cosmology Applications ," in *IPDPS '12*, 2012.

.

