# Characterization Research on I/O Improvements Targeting DISC and HPC Applications.

Laercio Pioli∗ , Eduardo C. Inacio† , Douglas D. J. de Macedo† , Victor Stroele ¨ ∗ , Jose Maria N. David ´ ∗ , Jean-Franc¸ois Mehaut ´ ‡ and Mario A. R. Dantas∗

∗*Federal University of Juiz de Fora*. Juiz de Fora, MG, Brazil {laerciopioli, victor.stroele, jose.nazar, mario.dantas}@ice.ufjf.br †*Federal University of Santa Catarina*. Florianopolis, SC, Brazil ´ eduardo.camilo@posgrad.ufsc.br ‡*Universite Grenoble Alpes* ´ . Saint-Martin-d'Heres, Is ` ere, France ` jean-francois.mehaut@univ-grenoble-alpes.fr

*Abstract*—Improvements in I/O architectures are becoming increasingly required nowadays. This is an essential point to complex and data intensive scalable applications. Data-Intensive Scalable Computing (DISC) and High-Performance Computing (HPC) applications frequently need to transfer data between storage resources. In the scientific and industrial fields, the storage component is a key element, because usually those applications employ a huge amount of data. Therefore, the performance of these applications commonly depends on some factors related to time spent in execution of the I/O operations. However, researchers, through their works, are proposing different approaches targeting improvements on the storage layer, thus, reducing the gap between processing and storage. Some solutions combine different hardware technologies to achieve high performance, while others develop solutions on the software layer. This paper aims to present a characterization model for classifying research works on I/O performance improvements for large scale computing facilities. Analysis over 36 different scenarios using a synthetic I/O benchmark demonstrates how the latency parameter behaves when performing different I/O operations using distinct storage technologies and approaches. *Index Terms*—DISC, HPC, I/O Performance, Characterization,

Storage Systems.

#### I. INTRODUCTION

The I/O bottleneck remains a central issue in High Performance Computing (HPC) due to the huge disparity gap between power processing and storage latency. This I/O bottleneck problem affects the performance of applications that move exabytes (EB) of computed or generated data between compute nodes (CN) and storage nodes (SN). Typically, these demanding applications are executed in clustered architectures. This fact makes the I/O performance a hot field of study and researchers are proposing solutions to improve the I/O architecture by different approaches. The performance of storage environments is very important in the cloud, big data and industrial scenarios where the amount of data and their manipulation is a well known challenge. Numerous solutions considering heterogeneous storage systems were proposed over the years [1] and [2]. Some of the most used approach in storage systems to support the I/O layer is utilizing *flash* devices, such as *SSD (Solid-State Disk)*, as a quick and auxiliary storage for *HDD (Hard Disk Drive)*. Software solutions to improve I/O performance on storage systems were also employed. Some of them focused on improving I/O considering better database and file system performance [3], [4], [5], [6] while others focusing on I/O schedulers [7], [8] and [9],

Classifying these improvements in a perspective that divide software components from hardware components, allows us to understand how these improvements have been built over the years and how it progresses. The usage of this characterization model, when publishing research works, allows us to direct future efforts towards subjects that really need attention. Therefore, reducing bottlenecks that hinder the entire development structure. For example, if through our classification we find that flash memory devices are getting little improvements and considering that hybrid storage systems uses flash-based devices in their architecture, we could use this model to understand that more proposals should be developed to fill this gap that reduces the hybrid storage systems evolution.

Therefore, the overall overview of the actual efforts could be divided into a macro view of three elements. It could be classified into a characterization model related to the I/O improvements. The two first elements are "software" and "hardware" and the junction of these previous elements would create a new element "storage system". Firstly, "software" investigations could be understood as an improvement where the object that is being proposed as a solution is an algorithm, method, framework or any programmable solution. Secondly, "hardware" investigations could be characterized as improvements when the object that is being proposed to improve is a physical component or something palpable. Finally, these two groups can relate and improve each other generating a new classification object "storage system".

The remainder of this paper is organized as follows. In Section II, we present a brief background related to DISC and High Performance I/O and Storage. We discuss some related works in the Section ??. The proposal of this paper is presented in Section III. In Section IV, we present the experimental environment used and the experimental results evaluated in the Grid'5000. Section V concludes this paper, summarizing this research work and outlining future works.

## II. BACKGROUND

DISC systems appeared due to the necessity to deal with a huge amount of data. Scientific applications used in science generate, collect and store an underwhelming volume of data. In most cases, these data need to be processed and organized through a system which could acquire, update and share the datasets in an organized way. Although DISC systems came to fulfill requirements with emphasis on data solution, they eventually perform sophisticated computations over these captured data. Concerning about data processing, some Big Data frameworks such as Apache Spark and Apache Hadoop are examples of tools to deal with DISC applications. These applications relies on powerful data processing operators such as Map, Reduce, Filters, etc [10]. In general, requirements related to data analysis and visualizations were not achieved by DISC systems because these environments were not designed for scientific applications.

Historically, HPC field has been mainly focused on processing-related topics, mostly due to the increasing processing demands of large-scale computational science applications. Such demands have motivated a great deal of research works, resulting in the development of novel methods and techniques aiming at improving the processing power available for these applications. At the same time, the availability of more powerful computing infrastructures has encouraged the investigation of even larger and more complex problems, resulting in the cycle as illustrated in Fig. 1.

![](_page_1_Figure_4.png)

Fig. 1: Evolution cycle of computational science demands.

Nowadays HPC systems consist of a very specialized and complex combination of hardware and software elements. Their design mainly focuses on providing high processing power for large scale distributed and parallel applications, even though low communication and data access latency are considered increasingly important requirements [11]. Fig. 2 presents an overview of a general infrastructure model commonly observed in many modern HPC environments. A main characteristic observed in these environments is the separation of compute and storage resources, which results in massive data movements through layers of the I/O path during the execution of a data-intensive application. Consequently, even in this simplified illustration, it can be noted the complexity of such environments.

In the past, some authors have proposed results in I/O optimization approaches considering the I/O stack as a whole.

![](_page_1_Figure_8.png)

Our initial search, referring to the contributions to the parallel I/O stack and workloads characteristics in huge infrastructures.

Boito et al. [12] present interesting research in a 5-year window on the parallel I/O for HPC environments. The authors focus on the parallel I/O and present the state of the art in I/O optimization approaches as much as in many subjects that the I/O stack is composed. Most proposals presented by the author consider solutions implemented on the software layer (e.g. caching/prefetching, I/O scheduling, Collective I/O, Requests aggregation, among others). However, the presented survey does not consider the importance of the wide variety of hardware technologies used by the storage nodes to save the data. In some cases they just mentioned the two more common devices used to store data (e.g. HDD and SSD).

Calzarossa et al. [13] presented a survey considering a characterization model but differently from the previous one they consider the importance of the workload characterization exploiting its importance in popular applications domains. Their focus is directed to workload from the web and with workloads associated with online social networks, video services, mobile apps and cloud computing infrastructure. Their proposed characterization model does not consider the three basic elements (e.g. software, hardware and storage systems) like our presented model. They present studies in a cloud computing infrastructure, but their concern to the characteristics of cloud workloads.

Finally, Traeger et al. [14] described and presented a survey considering a nine year study examining a range of file system and storage benchmarks. They surveyed a range of 106 file-system and storage-related research papers in this study. As in the previous related works, the authors did not consider hardware characteristics and how it can influence the performance in an evaluation process of a storage system.

### III. CHARACTERIZATION MODEL

A characterization model for classifying research works on I/O performance is presented in this section. Nowadays, the gap of development between CPU and storage technologies is too big, thus making the storage layer the bottleneck of the overall systems. Because of that, researchers are proposing different approaches targeting improvements on the storage layer. Some authors combine different hardware technologies to fill this issue, others develop solution on the software layer trying to improve the algorithms and systems to better fit the applications. There are also authors that are proposing new architectures and storage systems combining hardware devices and software applications through different approaches. Considering these observed characteristics, our model is composed by three main elements (i.e. software, hardware and storage systems) that represent these scenarios. With this approach, we believe that if researchers classify their papers before publishing, it could improve and save time by the others researchers when trying to improve objects on this field.

On our proposed model, as illustrated in Fig. 3, each circle means an element which is related with the author proposal object. The software circle symbolizes an improvement made by a researcher where the object that is being proposed as a solution is any programmable solution (e.g. algorithm, method, frameworks, etc). Hardware circle symbolizes an improvement made by a researcher where the object that is being proposed as a solution is any physical component or something palpable (e.g. device, chip, accessory, etc). The third element, storage systems, only receives improvements from the previous two elements. In this model we defined that a storage system should necessarily be composed of hardware and software elements. The first two elements on the down layer can relate each other in both direction and both of them can suggest solution as an object to improve the I/O performance on an entire storage systems platform.

![](_page_2_Figure_2.png)

Fig. 3: Characterization of I/O Performance Improvements.

Table I presents previous works targeting I/O improvements on storage systems, devices and software. Each arrow shown in Fig. 3 is related to a column shown in Table I.

There is no additional intention in the presentation of the works exposed in Table I besides showing that they have purposes in improving a similar class of objects. The amount of contributions shown in Table I has been reduced to satisfy the amount of page required. These papers are part of a systematic review we are performing that targets I/O improvement as much as in storage devices, software and storage systems in the last 10 years.

The first column *S2H-IO* which means *"Software solution to improve I/O performance on Hardware"* is composed of the following papers: Yang et al. [15] proposed a solution called

TABLE I: Papers Classification Targeting I/O Improvements.

| S2H-IO | H2H-IO | S2S-IO | H2S-IO | S2SS-IO | H2SS-IO |
| --- | --- | --- | --- | --- | --- |
| [15] | [16] | [17] | [18] | [19] | [20] |
| [21] | [22] | [23] | [24] | [25] | [26] |

WARCIP to tackle the write amplification problem which is an inherent physical property of flash memories devices. Chang et al. [21] present a novel I/O scheduling scheme, called MAP+, for embedded flash storage devices. These papers propose a *software* object to improve I/O performance on a device. Because of that, they could be characterized as a *software* solution to improve I/O performance on *hardware* device. The arrow that represents this subject in Fig. 3 leaves the red circle *software* and arrives in the green circle *hardware*.

The second column *H2H-IO* which means *"Hardware solution to improve I/O performance on Hardware"* is composed of the following papers: Kim et al. [16] proposed the insertion of the frequency-boosting interface chip (F-Chip) into the NAND multi-chip package (MCP) including a 16-die stacked 128Gb NAND flash. Kim et al. [22] proposed the design of FESSD which uses an on-chip access control memory (ACM) introducting any type of on-chip non-volatile memory into the micro-controller of an SSD. Differently from the previous one, the papers here propose a *hardware* object to improve I/O performance on another *hardware* device. The arrow that represents this subject in Fig. 3 leaves the green circle *hardware* and arrives in the same green circle *hardware* through an auto relation.

The third column S2S-IO which means *"Software solution to improve I/O performance on Software"* is composed of the following papers: Wu et al. [17] proposed a data placement method which provides databases with high I/O performance by considering an integrated mechanism and migration rule to move high-priority data between HDDs and SSDs. Yang et al. [23] proposed an approach aiming at solving duplication in VM disks. Content look-aside buffer (CLB) was provided and implemented on KVM hypervisor. The approach provides a redundancy-free virtual disk I/O and caching. These papers consider some *software* object as a *"solution"* to perform its improvement. It is important to notice that, although the improvements are from software to software, they take into account the storage technologies that they are using. The arrow that represents this subject in Fig. 3 leaves the red circle *software* and arrives in the same red circle *software*.

The fourth column H2S-IO which means *"Hardware solution to improve I/O performance on Software"* consider some *hardware* object as a *"solution"* to improve I/O performance of some *software*. This column is composed of the following papers: Nakashima et al. [18] improve I/O performance of a large scale DNA application using SSD device as a cache. Moon et al. [24] optimize the hadoop mapreduce framework with high-performance storage devices. In this case different hardware and technologies are used as solution to improve applications I/O performance. In Fig. 3 it is presented as the arrow that leaves the green circle *Hardware* and arrives in the red circle *Software*.

The fifth and sixth column are concerned about I/O improvements targeting storage systems. It is important to notice that in this characterization we consider *"Storage Systems"* as a group of technologies and software which work together and asynchronously. The fifth column S2SS-IO which means *"Software solution to improve I/O performance on Storage Systems"* relate improvements targeting I/O performance into a *storage system* through a software *"solution"*. This column is composed of the following papers: Zhou et al. [19] proposed an algorithm which makes better use of heterogeneous devices for storage systems and is based on consistent hashing. Du et al. [25] proposed a balanced partial stripe (BPS) write scheme to improve write performance of RAID-6 systems. In Fig. 3 these improvements are presented as arrow that leaves the red circle *software* and arrives in the blue circle *storage systems*.

Finally, the last column H2SS-IO which means *"Hardware solution to improve I/O performance on Storage Systems"* consider a *hardware* object as a *"solution"* to improve I/O performance of a *storage system*. They are explored below: Kannan et al. [20] proposed using a nonvolatile random access memory (NVRAM) to enhance the memory capacities of computing nodes. Each node has an additional Active NVRAM component. Bu et al. [26] introduces a Hybrid SSD approach that combines DRAM, phase changed memory (PCM) and flash memory into a hierarchical storage system. In Fig. 3 the arrow that leaves the green circle *hardware* and arrives in the blue circle *storage systems* represent these improvements.

### IV. EXPERIMENTAL ENVIRONMENT AND RESULTS

Our experimentation process analyzes the latency rate when performing I/O operation (e.g. read and write) in a huge experimental environment. It considers 10 different parameters and produce results from 36 different scenarios that we expose on this document. In this empirical process we are generating results that symbolizes research works which targets improvements of the I/O performance in the storage layer. This validating process intents to encourage the overall researchers to keep proposing solutions to fill this huge bottleneck that we have in those environments nowadays.

#### *A. Experimental Environment*

Experiments were carried out in the *dahu* cluster, from the Grid'5000 testbed. Each of the 32 nodes is equipped with 2 CPUs (16 cores/CPU), 192 GiB RAM, 240 GB SSD, 480 GB SSD, and a 4 TB HDD. A CentOS 7 (kernel 3.10.0) operating system image was deployed on each node, with an ext4 file system. In these experiments, 16 nodes were used as compute nodes (CNs), generating I/O requests using the IOR-Extended (IORE) performance evaluation tool [27] over MPICH 3.0.4, and 8 nodes as storage nodes (SNs), into which an OrangeFS 2.9.7 parallel file system (PFS) was deployed.

## *B. Experiment Factors Definition*

In this section, Table II presents the factors we used to perform the experiments. We also relate some of these factors with the elements presented in Fig. 3. In this research we consider three hardware approaches to store data and metadata because we believe that the way you organize those technologies might influence on the performance of your application. This factor relates the hardware storage devices used in the experiment with the green circle *Hardware* in Fig. 3. Many contributions are performed by researchers to improve schedulers because I/O schedulers play an essential role on those environments. This factor relates schedulers to the red circle *(software)* presented in Fig. 3. The number of tasks participating in the test was also considered in this experimentation. Finally, another factor was considered on the experimental effort, relating to data access pattern.

TABLE II: Factors Considered in this Experiment

| Factor | Values |
| --- | --- |
| Storage Approach | HDD, HDD+SSD, SSD |
| Linux Scheduler | CFQ, noop, deadline |
| Number of Tasks | 32, 64 |
| Access Pattern | sequential, random |

## *C. Executing IORE Benchmark*

IORE benchmark is a unified and flexible tool for performance evaluation of modern high-performance parallel I/O software stacks and storage systems [27]. In each experiment we configured the scheduler we used on data servers (CFQ, Deadline and Noop), the way we were storing data and metadata on the storage devices (data and metadata on HDD, data on HDD and metadata on SSD, data and metadata on SSD) and the workloads characteristics we had set into the IORE configuration file ("num tasks" and "access pattern"). In the IORE configuration file, we set up to output 4 scenarios, named as a number in a column "run id", in which we commuted changing the parameters "num tasks" and "access pattern". The parameters possibility were 32 and 64 for the num tasks and "random" and "sequential" to the "access pattern". The data size we use on this experiment were 32 MiB with a request size of 2 MiB on each I/O operation process.

## *D. Experimental Results and Discussion*

Results from our experimental effort are presented in Fig. 4. Although these results could be analyzed by many different perspectives, they are discussed considering the storage approach, namely, HDD, HDD+SSD, and SSD. In each bar plot, the y-axis refers to the average Latency in MiB/s and the x-axis refers to scenarios combining different numbers of tasks and access patterns. Further, hatched bars denote read operations and non-hatched bars denote write operations. Finally, different colors were used to contrast results observed with distinct I/O schedulers.

Figures 4a, 4b and 4c present the latency average for the I/O requests according to the used storage approach. It is possible to verify that, almost in all cases the HDD-only approach latency for the write operation was the worst independently from the used scheduler. The excepted scenarios where this fact is not true is in configuration 32/Seq and 64/Seq using CFQ scheduler. In these cases, the hybrid approach was worst than the HDD-only approach. In 64/Ran configuration for the hybrid storage approach, the deadline scheduler also presented this comportment. In all other cases, the HDD-only storage environment had the highest latency. We also noticed that the write latency for the SSD-only storage approach was the best one in all configurations. Some possible factors could lead us to understand these results. Actually, reads can be faster than writes, mainly, because, sometimes, they are made on date already read into memory, rather than doing it from disk. I/O operations in HDDs are very costly due to the inherent mechanical components inside the device. Factors related with the operating system and the way it handles hardware can have also influenced results. Another factor we could suggest is the way the file system performs operations. Usually, to read a file, the file system just traverses the directory tree until the data and then read the file loading it into memory. To write a file, the same operation through the tree should be performed and after finding the path, write the data to the desirable local, but, differently from the read operation, the file system should update the metadata related to the written file.

To analyse the read operation, we summarized Fig. 4 through a perspective where we can verify how each Linux scheduler behaved according to the used storage approach. Tables III and IV presented the most expressive obtained results. We classify, in each case, how the schedulers behave in each storage approach. Each presented figure describes an storage approach usage and it is directly related to one column in each Table. For instance, the values presented in Fig. 4a shown the latency using the only-HDD approach to store data and metadata. These values were distributed among the four Tables IIIa,IIIb, IVa and IVb throughout the column HDD. These expressive results were distributed respecting each task number and access pattern blocks. It allowed us to compare the Linux schedulers latency performance considering each storage approach side by side. The numbers within each table mean: (1) the slowest latency, (2) the intermediate latency and (3) the highest latency. We want to verify which storage scenario the scheduler had its better latency performance. It allow us to verify in which storage scenario the scheduler had its better latency performance.

Table III presents the values considering number of tasks equal to 32. Table IIIa refers to sequential access pattern over 32 task number size and it indicates that the schedulers present low latency over the hybrid approach. Interestingly, we also noticed that the schedulers does not presented the best latency rate when using the SSD-only storage approach. Over the random access pattern, Table IIIb indicates that the schedulers performed well using the SSD-only storage approach. We also noticed that the HDD-only approach was the worst one, presenting the highest latency rate.

Table IV presents the values considering number of tasks equal to 64. Table IVa relates values for sequential access pattern Over 64 task number size, it indicates that HDDonly storage approach presented the highest latency for all schedulers. We also noticed that the hybrid storage approach was the approach that presented the lowest latency. Table IVb is relates to a random access pattern. Curiously, it presented the same pattern for all approaches being the hybrid the one that presented the lowest latency rate. As the pattern presented on the Table IVa, Table IVb also presented the highest latency for the HDD-only approach in all cases.

TABLE III: Results grouped by 32 number of tasks size

|  | HDD | HDD/SSD | SSD | HDD |  | HDD/SSD | SSD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CFQ | 2 | 1 | 3 | CFQ | 3 | 2 | 1 |
| Deadline | 1 | 2 | 3 | Deadline | 3 | 1 | 2 |
| Noop | 2 | 1 | 3 | Noop | 3 | 2 | 1 |
|  | (a) 32/Seq |  |  | (b) 32/Ran |  |  |  |

TABLE IV: Results grouped by 64 number of tasks size

|  | HDD | HDD/SSD | SSD | HDD |  | HDD/SSD | SSD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CFQ | 3 | 1 | 2 | CFQ | 3 | 1 | 2 |
| Deadline | 3 | 2 | 1 | Deadline | 3 | 1 | 2 |
| Noop | 3 | 1 | 2 | Noop | 3 | 1 | 2 |
|  | (a) 64/Seq |  |  | (b) 64/Ran |  |  |  |

(a) 64/Seq

#### V. CONCLUSION

The necessity to transfer extensive quantities of data to storage resources are becoming an issue for DISC and HPC applications. This happens due to the existing I/O bottleneck when transferring computed data to storage devices. However, researchers, through research works, are proposing different approaches targeting improve the storage layer performance decreasing then this I/O architecture problem. In this paper we presented an I/O characterization model for classifying research works on I/O performance improvements. We consider that the actual effort is composed of three basic elements divided into a macro view of software, hardware and storage systems. We also present a set of experiments executed inside the Grid'5000. We show how the latency operation behaves over 36 different scenarios defined by some factors and how it can undergo many variations if we take into account the presented factors evaluated in the experiments. In order to improve these research, we intend to finish a 10 years survey which consider more than five hundred research works and classify all them using our characterization model presented on this paper. Although our results permit many different analysis, we concentrated and presented results considering the selected schedulers and the used storage scenario. For future work, we intend to share a 10 years survey which consider more than five hundred research works and classify all them using the presented characterization model. Furthermore, we intend to perform experiments in a large cloud environment considering different storage technologies and software approaches.

#### ACKNOWLEDGMENT

Experiments presented in this paper were carried out using the Grid'5000 testbed, supported by a scientific interest group hosted by Inria and including CNRS, RENATER

![](_page_5_Figure_0.png)

Fig. 4: Latency analysis according to the storage data approach

and several Universities as well as other organizations (see https://www.grid5000.fr). We also would like to thank the Federal University of Juiz de Fora (UFJF), CNPq, CAPES, FAPEMIG, PTI-LASSE and INESC P&D Brazil in SIGOM project that support in part this study.

#### REFERENCES

- [1] J. Zhang, F. Meng, L. Qiao, and K. Zhu, "Design and implementation of optical fiber ssd exploiting fpga accelerated nvme," *IEEE Access*, vol. 7, pp. 152944–152952, 2019.
- [2] J. Zhou, W. Xie, J. Noble, K. Echo, and Y. Chen, "Suora: A scalable and uniform data distribution algorithm for heterogeneous storage systems," in *IEEE Int. Conf. on Net., Arch. and Storage*, pp. 1–10, IEEE, 2016.
- [3] H. Kim, H. Y. Yeom, and Y. Son, "An i/o isolation scheme for key-value store on multiple solid-state drives," in *2019 IEEE 4th International Workshops on Foundations and Applications of Self* Systems (FAS** W), pp. 170–175, IEEE, 2019.
- [4] C.-H. Wu, C.-W. Huang, and C.-Y. Chang, "A data management method for databases using hybrid storage systems," *ACM SIGAPP Applied Computing Review*, vol. 19, no. 1, pp. 34–47, 2019.
- [5] X. Zhang, Y. Wang, Q. Wang, and X. Zhao, "A new approach to double i/o performance for ceph distributed file system in cloud computing," in *2019 2nd International Conference on Data Intelligence and Security (ICDIS)*, pp. 68–75, IEEE, 2019.
- [6] Y. Fan, Y. Wang, and M. Ye, "An improved small file storage strategy in ceph file system," in *2018 14th International Conference on Computational Intelligence and Security (CIS)*, pp. 488–491, IEEE, 2018.
- [7] T. Yang, P. Huang, W. Zhang, H. Wu, and L. Lin, "Cars: A multi-layer conflict-aware request scheduler for nvme ssds," in *2019 Design, Automation & Test in Europe Conference & Exhibition (DATE)*, pp. 1293– 1296, IEEE, 2019.
- [8] D. Park, D. H. Kang, S. M. Ahn, and Y. I. Eom, "The minimaleffort write i/o scheduler for flash-based storage devices," in *2018 IEEE International Conference on Consumer Electronics (ICCE)*, pp. 1–3, IEEE, 2018.
- [9] G. Yan, R. Chen, Q. Guan, and Z. Feng, "Dls: A delay-life-aware i/o scheduler to improve the load balancing of ssd-based raid-5 arrays," in *2019 IEEE 21st International Conference on High Performance Computing and Communications; IEEE 17th International Conference on Smart City; IEEE 5th International Conference on Data Science and Systems (HPCC/SmartCity/DSS)*, pp. 2445–2450, IEEE, 2019.
- [10] P. Valduriez, M. Mattoso, R. Akbarinia, H. Borges, J. Camata, A. Coutinho, D. Gaspar, N. Lemus, J. Liu, H. Lustosa, *et al.*, "Scientific data analysis using data-intensive scalable computing: The scidisc project," 2018.
- [11] R. Lucas, J. Ang, K. Bergman, S. Borkar, W. Carlson, L. Carrington, G. Chiu, R. Colwell, W. Dally, J. Dongarra, *et al.*, "Top ten exascale research challenges," *DOE ASCAC subcommittee report*, pp. 1–86, 2014.
- [12] F. Z. Boito, E. C. Inacio, J. L. Bez, P. O. Navaux, M. A. Dantas, and Y. Denneulin, "A checkpoint of research on parallel i/o for highperformance computing," *ACM Computing Surveys*, vol. 51, no. 2, pp. 1– 35, 2018.

- [13] M. C. Calzarossa, L. Massari, and D. Tessera, "Workload characterization: A survey revisited," *ACM Computing Surveys (CSUR)*, vol. 48, no. 3, pp. 1–43, 2016.
- [14] A. Traeger, E. Zadok, N. Joukov, and C. P. Wright, "A nine year study of file system and storage benchmarking," *ACM Transactions on Storage (TOS)*, vol. 4, no. 2, pp. 1–56, 2008.
- [15] J. Yang, S. Pei, and Q. Yang, "Warcip: write amplification reduction by clustering i/o pages," in *ACM Int. Conf. on Systems and Storage*, pp. 155–166, ACM, 2019.
- [16] H.-J. Kim, J.-D. Lim, J.-W. Lee, D.-H. Na, J.-H. Shin, C.-H. Kim, S.-W. Yu, J.-Y. Shin, S.-K. Lee, D. Rajagopal, *et al.*, "7.6 1gb/s 2tb nand flash multi-chip package with frequency-boosting interface chip," in *IEEE Int. Solid-State Circuits Conf.*, pp. 1–3, IEEE, 2015.
- [17] C.-H. Wu, C.-W. Huang, and C.-Y. Chang, "A priority-based data placement method for databases using solid-state drives," in *Proceedings of the 2018 Conference on Research in Adaptive and Convergent Systems*, pp. 175–182, ACM, 2018.
- [18] K. Nakashima, J. Kon, and S. Yamaguchi, "I/o performance improvement of secure big data analyses with application support on ssd cache," in *Int. Conf. on Ubiq. Inf. Management and Comm.*, p. 90, ACM, 2018.
- [19] J. Zhou, Y. Chen, and W. Wang, "Atributed consistent hashing for heterogeneous storage systems.," in *PACT*, pp. 23–1, 2018.
- [20] S. Kannan, A. Gavrilovska, K. Schwan, D. Milojicic, and V. Talwar, "Using active nvram for i/o staging," in *Int. Work. on Petascale Data Analytics: challenges and opportunities*, pp. 15–22, ACM, 2011.
- [21] C. Ji, L.-P. Chang, C. Wu, L. Shi, and C. J. Xue, "An i/o scheduling strategy for embedded flash storage devices with mapping cache," *IEEE Trans. on Computer-Aided Design of Integrated Circuits and Systems*, vol. 37, no. 4, pp. 756–769.
- [22] J. Lee, K. Ganesh, H.-J. Lee, and Y. Kim, "Fessd: A fast encrypted ssd employing on-chip access-control memory," *IEEE Computer Architecture Letters*, vol. 16, no. 2, pp. 115–118, 2017.
- [23] C. Yang, X. Liu, and X. Cheng, "Content look-aside buffer for redundancy-free virtual disk i/o and caching," in *ACM SIGPLAN Notices*, vol. 52, pp. 214–227, ACM, 2017.
- [24] S. Moon, J. Lee, X. Sun, and Y.-s. Kee, "Optimizing the hadoop mapreduce framework with high-performance storage devices," The *Journal of Supercomputing*, vol. 71, no. 9, pp. 3525–3548, 2015.
- [25] C. Du, C. Wu, J. Li, M. Guo, and X. He, "Bps: A balanced partial stripe write scheme to improve the write performance of raid-6," in *IEEE Int. Conf. on Cluster Computing*, pp. 204–213, IEEE, 2015.
- [26] K. Bu, M. Wang, H. Nie, W. Huang, and B. Li, "The optimization of the hierarchical storage system based on the hybrid ssd technology," in *Int. Conf. on Intel. Syst. Design and Eng. App.*, pp. 1323–1326, IEEE, 2012.
- [27] E. C. Inacio and M. A. Dantas, "Iore: A flexible and distributed i/o performance evaluation tool for hyperscale storage systems," in *2018 IEEE Symposium on Computers and Communications (ISCC)*, pp. 01026–01031, IEEE, 2018.

