# I/O Performance Evaluation of Large-Scale Deep Learning on an HPC System

Minho Bae1 , Minjoong Jeong2 , Sangho Yeo1 , Sangyoon Oh1 , and Oh-Kyoung Kwon2 ∗

1 Computer Engineering, Ajou University, Suwon, Republic of Korea. 2 Supercomputing Department, Korea Institute of Science and Technology Information, Daejeon 34141, Republic of Korea.

*Abstract***—Recently, deep learning has become important in diverse fields. Because the process requires a huge amount of computing resources, many researchers have proposed methods to utilize large-scale clusters to reduce the training time. Despite many proposals concerning the training process for large-scale clusters, there remain areas to be developed. In this study, we benchmark the performance of Intel-Caffe, which is a generalpurpose distributed deep learning framework on the Nurion supercomputer of the Korea Institute of Science and Technology Information. We particularly focus on identifying the file I/O factors that affect the performance of Intel-Caffe, as well as a performance evaluation in a container-based environment. Finally,**  to the **best of our knowledge, we present the first benchmark results for distributed deep learning in the container-based environment for a large-scale cluster.**

*Keywords-component; distributed deep learning; large-scale cluster; HPC; Intel-Caffe; large mini-batch*

#### I. INTRODUCTION

Recently, a boom in deep learning (DL) has occurred, as a result of advances in DL algorithms as well as big data. Because DL with large-scale data requires a vast amount of computation, there has been considerable research on reducing the training time using the massive computing capacities of supercomputers and distributed DL frameworks. For example, Goyal et al. [1] and You et al. [2] completed the training processes of ResNet-50 on 256 NVIDIA Tesla P100 GPUs and the 2048 KNL CPU cluster within one hour and 20 minutes, respectively.

However, the currently popular distributed DL frameworks were originally designed for GPU cluster environments, and they are not optimized for CPU clusters, which yield better scalability on large-scale nodes. To address this issue, researchers and vendors have developed optimized versions of DL frameworks to enhance their performances on CPU clusters. For example, *Intel-Caffe* has achieved an enhanced performance for a distributed DL framework on a CPU cluster [3]. Many *Intel-Caffe* benchmarks have been obtained on CPU clusters [4, 5, 6, 7] by efficiently exploiting the architecture of a CPU cluster using the framework.

However, previous benchmarks are insufficient to provide knowledge and insights into large-scale CPU clusters because they focus on evaluation in an ideal environment for DL. More specifically, these were benchmarked in clusters in which all computing nodes have sufficient local disk space to store all training data. However, clusters tend to have less local disk space for training data. Thus, we need to conduct an in-depth analysis of the factors that affect the performance in a real cluster environment, where training data is loaded from a distributed file system.

In addition, many recent large-scale clusters adopt containerbased technology to achieve full control of the user environment. Because a DL framework has many package dependencies and version updates, it is difficult to manage in a large-scale cluster environment. Without a container, we require help from an administrator to manage corresponding packages. This can be avoided with a container by placing the packages within it. There are benchmarks that verify performances in a container-based environment at a small-scale cluster [8, 9, 10], but so far none of the studies evaluate the large-scale distributed DL performance in a container-based environment.

In this paper, we present our benchmark result for a distributed DL framework on the Nurion supercomputer of the Korea Institute of Science and Technology Information, consisting of 8,305 compute nodes, built on an Intel Xeon Phi Processor 7250 and the Intel Omni-Path Architecture. The computing nodes of Nurion have no local disks and are mounted on the Lustre file system. We conducted benchmarking of *Intel-Caffe* on the Nurion supercomputer, which provides the best performance among distributed DL frameworks on CPU-based clusters [5]. Furthermore, we performed benchmarking on the Lustre file system using a mounted Singularity system designed for the high-performance computing (HPC) environment [11].

The main contributions of this paper are summarized as follows:

- Identification of the file I/O factors that affect the performance of a distributed deep learning framework.
- Performance study of a distributed deep learning framework on a container-based HPC system.
- Overall performance analysis, in terms of the strong scalability of Intel-Caffe on the Nurion supercomputer.

The remainder of this paper is organized as follows. In Section Ⅱ, we review previous benchmark results. Then, we present and discuss our benchmark results in Section Ⅲ. Finally, we conclude the paper in Section Ⅳ.

#### II. PREVIOUS BENCHMARKS

There exist previous DL benchmarks on CPU clusters using *Intel-Caffe*, including that of Awan et al. [4]. In their research, the authors compared its performances with an NVIDIA GPU and a KNL node using AlexNet [14] and ResNet [15]. It was found that a KNL node with *Intel-Caffe* [3] performed twice as well in terms of the training time compared with an NVIDIA K40 GPU. However, the benchmark shows that a KNL node exhibits inferior overall performance for AlexNet than the NVIDIA P100 GPU. Zhang et al. [5] presented an additional benchmark on the Stempede2 supercomputer in Texas Advanced Computing Center. In this benchmark, a KNL node is found to be 1.8–2.3 times faster for *Intel-Caffe* than an NVIDIA K40 GPU. However, the KNL node was found to be 1.2–3.7 and 2.3 times slower than an NVIDIA K40 GPU for *MxNet* [13] and *TensorFlow* [12], respectively. Although both benchmarks provide a well-organized analysis of the DL performance on a CPU cluster using *Intel-Caffe*, they are insufficient to identify the file I/O factors that affect the performance of a distributed DL, because they focus instead on an overall performance evaluation.

Some researchers have studied the file I/O performance in distributed DL frameworks [16-18]. To improve the I/O performance, Zhang et al. [16] proposed a shared file system based on a profile study on distributed DL I/O behavior, and Pumma et al. [17] proposed an optimized I/O algorithm based on the data access pattern. Chien et al. [18] presented a wellorganized analysis of the file I/O performance using *TensorFlow*. However, they did not discuss the factors that affect the file I/O performance in a DL framework.

#### III. BENCHMARK RESULT AND DISCUSSION

In this section, we present four benchmark results for *Intel-Caffe* on the Nurion supercomputer. The following benchmarks were conducted: 1) a performance comparison of DL training between the Lustre file system and a local disk; 2) benchmarking on training data with different characteristics; 3) a performance comparison of *Intel-Caffe* between the native and Singularity environments; and 4) large-scale benchmarking of *Intel-Caffe*.

We evaluate the performances for image classification applications with both AlexNet and ResNet-50. AlexNet and ResNet-50 have different scaling ratios [2]. For AlexNet, the volume of communication (i.e., the number of parameters) and computations per each iteration (i.e., flops per image) are 61 million and 1.5 billion, respectively. On the other hand, for ResNet-50, the corresponding values are 25 million and 7.7 billion, respectively. Thus, ResNet-50 exhibits better scalability. We employed ImageNet-1K as the dataset [19]. When training the ImageNet dataset, we have two different options: an external database (LMDB, LevelDB, HDF5, etc.) and an image source. Because LMDB [20] is known to be faster than other databases, through the *mmap* function, we conduct experiments using LMDB. It would be better to perform DL on the local-disk in the computing node for a performance comparison with the Lustre file system. However, the nodes of Nurion have no local disk; therefore we set up a KNL testbed. This consists of four KNLs, each with an 80 GB local disk.

# A. *Comparison Between a Local Disk and the Lustre File System*

We compared the training performance for the Lustre file system (stripe count four) and the local disk with both Resnet-50 (512 mini-batch size) and AlexNet (960 mini-batch size) on the KNL testbed. The training data was reduced to a light ImageNet LMDB (~71 GB with 38,000 images) from ImageNet-1K LMDB, owing to the limitations of a local-disk capacity of ~80 GB on the KNL testbed.

In general, the DL training process requires vast memory space. In addition, a larger mini-batch size requires higher memory usage for training. Storing the training data in memory has advantages and disadvantages. In an environment with a large number of computing nodes, memory shortage problems are unlikely, because the cluster is able to distribute the training data across computing nodes. However, in a small or typical cluster, memory problems may occur when storing the training data in memory. *Intel-Caffe* is a general-purpose framework designed to read the training data from disk. Accordingly, the performance of *Intel-Caffe* is significantly affected by the file I/O properties, because a training process requires reading a large number of training samples from disk. To alleviate this problem, *Intel-Caffe* is implemented to overlap the file I/O overhead for reading the training data with the training computations. At each iteration of the training process, the training data for the next iteration is pre-fetched. As a consequence, the file I/O in DL training performed at every iteration, and so it is important to analyze the I/O in terms of the image throughput for each iteration. Fig. 1 illustratesthe number of processed images per second during 1000 training iterations, where the training time with Lustre is 1.4 times slower than that with the local-disk, owing of the bandwidth difference between the local disk and Lustre file system.

In addition, to measure the file I/O bottleneck we assume that the file I/O performance is proportional to the difference between the image throughput per second with and without disk I/O. In addition, we define an ideal image throughput using the number of processed images during the training time without disk I/O. To verify the ideal image throughput, we performed the experiment on the KNL testbed where the image is read from memory. Through this experiment, we verified that the training times of AlexNet and ResNet-50 without disk I/O are ~0.375 s and ~1.620 s, respectively. Converting these training times to image throughput per second, the ideal image throughputs per second on four KNLs are roughly 2560 and 316 for AlexNet and ResNet-50, respectively. As depicted in Fig. 1, the ideal image

![](_page_1_Figure_10.png)

Fig. 1. Image throughput according to the iteration number with ResNet-50 and AlexNet in a native environment

throughput was not achieved with the experimental settings, meaning that there are non-trivial file I/O bottleneck overheads. In addition, we can observe that image throughput per second steeply increases at the end of each epoch, where the numbers of iterations per epoch are 742 and 395 for ResNet-50 and AlextNet, respectively. In other words, the file I/O bottleneck is decreased at the end of each epoch. This is because some of the previously loaded images come directly from the page cache in memory. If all images can be loaded from the page cache, then there may be no performance difference between Lustre and the local disk at the same iteration.

# B. *Page Cache Performance*

To improve the disk I/O performance, most operating systems exploit the area of memory called the page cache. If a read request of a user-level program falls in the page cache area, then data can be retrieved from the page cache relatively quickly compared to a slower disk, resulting in an improved file I/O performance. However, it is difficult to fully exploit the page cache in a distributed DL framework, because the entire dataset is distributed across computing nodes. Each node is only responsible for storing a subset of the entire dataset in the page cache. Meanwhile, to improve the accuracy most DL frameworks adopt a shuffling process, which makes each node train a different mini-batch at every epoch. This shuffling process yields a reduction in the effect of the page cache because the possibility of reading training data from the page cache rather than from the disk is decreased. To clarify the effect of the page cache with shuffling, we measure the performance for a nonshuffling experiment, where we loaded the same training data for every epoch with AlexNet. AlexNet is more affected by the file I/O overhead than ResNet-50. In the non-shuffling experiment, the performance of Lustre was almost the same as that of the local-disk after first epoch. This means that no further disk I/O bottleneck occurs, regardless of file system, as all training data can be retrieved from the page cache in memory.

To analyze the extent of the page cache effect on the file I/O performance, we performed an experiment with four different training datasets for AlexNet with the Lustre file system on the KNL testbed. Furthermore, we analyzed the effects of the number of images and data size per image on the DL performance. Table Ⅰ describes the LMDB dataset utilized in this experiment. If stored in raw LMDB, all images have the same data size per image. However, in JPG LMDB the data size per image varies, owing to different compression ratios. A JPG LMDB is 6.4 times smaller on average than a raw LMDB. Fig. 2 illustrates the numbers of processed images per second for the four different training datasets.

We claim that the page cache effect is confirmed by the results of this experiment. All images are trained without duplication within the same epoch. Thus, the page cache effect is almost constant at the same epoch, because already trained

|
|  |

| Name | # of Image | Data Size | Average Data size | # of iteration | Data |  |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  | per image | in one epoch | Type |  |
| D1 | 380,000 | 71.05 GB | 196.08 KB | 395 | Raw |  |
| D2 | 190,000 | 35.53 GB | 196.08 KB | 197 | Raw |  |
| D3 | 1,281,167 | 40 GB | 30.67 KB | 1334 | JPG | Fig. 3. Image throughputs according to the iteration number with (a) ResNet |
| D4 | 600,000 | 18.69 GB | 30.60 KB | 625 | JPG |  |

![](_page_2_Figure_7.png)

Fig. 2. Image throughputs of four different training datasets according to the iteration number with AlexNet

images are not used as input data. On the other hand, as the number of epochs increases the training process exploits the page cache, because the previously input images that are stored in the page cache are trained again on each node. In Fig. 2, we observe that the page cache effect makes the image throughput increase at the end of each epoch, and is almost constant at the same epoch.

Next, we analyze the results of this experiment in terms of two factors: the number of images and data size per image. As shown in Fig. 2, D1 has the same average size per image as D2. However, D2 yields a higher image throughput than D1. In other words, even though the data size per image is similar, there is a higher image throughput for a smaller number of images. This is because D2 takes advantage of a page cache that is two times larger than D1. The length of an epoch, which is a metric describing how much the page cache affects the file I/O performance, is proportional to the number of images. As a consequence, D2 can quickly achieve the ideal image throughput, because it has half the number of images of D1. D3 and D4 exhibit a similar pattern. However, they achieved the ideal image throughput after a few epochs. We reason that this is because they can read almost the entire mini-batch for the following iterations during the training computation. Even if the number of stored images in the page cache is small, the data size per image

![](_page_2_Figure_11.png)

50 and (b) AlexNet in the native and Singularity environments

438

![](_page_3_Figure_0.png)

Fig. 4. Strong scaling efficiency for up to 2048 KNLs of the Nurion system using ResNet-50 with a 32K mini-batch

is also relatively small. Therefore, we claim that the file I/O bottleneck decreases as the data size per image and number of images decrease.

#### C. *Container-Based Environment*

We evaluate the DL performance in a container-based Singularity (version 2.4.2) environment with both Resnet-50 and AlexNet on the KNL testbed. Fig. 3 depicts the number of images processed per second during 1000 training iterations. The image throughput with Singularity is almost the same as that in the native environment. The performances of the Luster file system and local-disk using Singularity are also similar to the results in the native environment. Through this experiment, we found that the overhead of the Singularity environment is minimal.

## D. *Large-Scale Deep Learning Benchmark*

In this experiment, we demonstrate the strong scalability of the distributed DL performance on the Nurion system. To clarify the effect of scalability, we only consider ResNet-50, which has a higher scale ratio than AlexNet. Furthermore, we do not employ data augmentation, as the goal of this experiment is not to obtain the highest accuracy. We employ the D4 training data for the Lustre file system (stripe count 160). Because we focus on evaluating the I/O performance of *Intel-Caffe*, rather than the mini-batch size, we employ LARS algorithms with a 32K minibatch size (the maximum size while maintaining the accuracy for 90 epochs). Fig. 4 illustrates the strong-scaling efficiency. We obtained a training time of 23 minutes while satisfying the non-data augmentation baseline accuracy (73.0%). With 2048 KNLs, we obtained a scaling speedup of ~2.60× compared to 512 KNLs. The results of this experiment also demonstrate that the image throughput is increased owing to the page cache effect, even if disk I/O occurs.

#### IV. CONCLUSION

We evaluated the performance of *Intel-Caffe*, a well-known distributed DL framework, on the Nurion supercomputer. We conducted benchmarking of the distributed DL framework on both a Lustre file system and container-based environment in a large-scale CPU environment. Through the benchmark, we determined that the DL training process in a container-based environment has a minimal overhead. We also found that the page cache affects the performance of the DL framework. If we alter the shuffle algorithm to fully utilize the page cache, then the file I/O bottleneck can be alleviated. Finally, we demonstrated a large-scale DL benchmark on a container-based environment for the first time. Using 2048 KNLs, we obtained a training time of 23 minutes on a container-based environment with a Lustre file system.

## ACKNOWLEDGMENT

This research was supported by Basic Science Research Program through the National Research Foundation of Korea(NRF) funded by the Ministry of Education (NRF-2018R1D1A1B07043858) and the supercomputing department at KISTI (Korea Institute of Science and Technology Information)(K-19-L02-C07-S01)

#### REFERENCES

- [1] P. Goyal, P. Dollár, R. B. Girshick, P. Noordhuis, L. Wesolowski, A. Kyrola, A. Tulloch, Y. Jia, K. He, "Accurate large minibatch SGD: training imagenet in 1 hour", abs/1706.02677, 2017.
- [2] Y. You, Z. Zhang, C.J. Hsieh, J. Demmel and K. Keutzer, "ImageNet Training in Minutes," International Conference on Parallel Processing(ICPP), 2018.
- [3] Intel, "intel/caffe," GitHub, 2019. [Online]. Available: https://github.com/intel/caffe. [Accessed: 24-Feb-2019].
- [4] A. A. Awan, H. Subramoni, and D. K. Panda, "An In-depth Performance Characterization of CPU- and GPU-based DNN Training on Modern Architectures," Machine Learning on HPC Environments(MLHPC), 2017
- [5] Z. Zhang, W. Xu, N. Gaffney and D. Stanzione, "Early results of deep learning on the stampede2 supercomputer", Technical Report, 2017
- [6] S. L. Smith, P. Kindermans, Q. V. Le, "Don't decay the learning rate increase the batch size", abs/1711.00489 (2018)
- [7] V. Codreanu, D. Podareanu, and V. Saletore, "Scale out for large minibatch SGD: Residual network training on ImageNet-1K with improved accuracy and reduced time to train", abs/1711.04291, 2017.
- [8] S. Ceesay, A. Barker and B. Varghese, "Plug and play bench: Simplifying big data benchmarking using containers", IEEE International Conference on Big Data (Big Data), 2017
- [9] R Rizki, A Rakhmatsyah, and M. A. Nugroho, "Performance analysis of container-based hadoop cluster: OpenVZ and LXC", International Conference on Information and Communication Technology, 2016
- [10] G. F. Zaki, J. M. Wozniak, J. Ozik, N. Collier, T. Brettin and R. Stevens, "Portable and Reusable Deep Learning Infrastructure with Containers to Accelerate Cancer Studies", IEEE/ACM 4th International Workshop on Extreme Scale Programming Models and Middleware (ESPM2), 2018
- [11] G. M. Kurtzer, V. Sochat, and M. W. Bauer, "Singularity: Scientific containers for mobility of compute," PloS one, vol. 12 , 2017.
- [12] Google, "tensorflow/tensorflow," GitHub, 2019. [Online]. Available: https://github.com/tensorflow/tensorflow [Accessed: 24-Feb-2019].
- [13] Apache, "apache/incubator-mxnet" GitHub, 2019. [Online]. Available: https://github.com/apache/incubator-mxnet [Accessed: 24-Feb-2019].
- [14] A. Krizhevsky, I. Sutskever, and G. E. Hinton, "ImageNet classification with deep convolutional neural networks," Communications of the ACM, vol. 60, no. 6, pp. 84–90, 2017.
- [15] K. He, X. Zhang, S. Ren, and J. Sun, "Deep Residual Learning for Image Recognition," IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016.
- [16] Z. Zhang, U. Manor, and G. Merlo, "FanStore: Enabling Efficient and Scalable I/O for Distributed Deep Learning", abs/1809.10799 (2018).
- [17] S. Pumma, M. Si, W. C. Feng, and P. Balaji, "Towards Scalable Deep Learning via I/O Analysis and Optimization", 19th International Conference on High Performance Computing and Communications (HPCC), vol. 2018, pp. 223–230, 2018.
- [18] S. W. D. Chien, S. Markidis, C. P. Sishtla, L. Santos, P. Herman, S. Narasimhamurthy and E. Laure, "Characterizing Deep-Learning I / O Workloads in TensorFlow", abs/1810.03035, 2018.
- [19] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, L. Fei-Fei, "Imagenet: A large-scale hierarchical image database", IEEE Conference on Computer Vision and Pattern Recognition, pp. 248-255, 2009.
- [20] H, Chu. "MDB: A Memory-Mapped Database and Backend for OpenLDAP", In Proceedings of the 3rd International Conference on LDAP, 2011

