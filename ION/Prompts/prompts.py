from IONPro.Generator.Utils.sources import extract_and_add_source_root, prepend_source_key_with_root
from .response_formats import RAGDiagnosis
import json
DARSHAN_HELPFUL_CONTEXT = (
    "Note that, for the rank data column, -1 indicates that the file is shared. "
    "For other data columns, -1 indicates that the data is not available and the value should be ignored."
    "Also, note that requests from the MPI-IO module are translated to POSIX requests, but the broader context will already have removed any double counting of requests."
)

SOURCE_CORRECTION_EXAMPLES = (
    "EXAMPLE ONE: \n"
    "Raw Text: The high number of write operations can lead to increased latency and degraded performance as indicated by source 4, especially if the underlying storage system is not capable of efficiently handling such a high throughput of writes. [4, 9] \n"
    "Corrected Text: The high number of write operations can lead to increased latency and degraded performance as indicated by [4], especially if the underlying storage system is not capable of efficiently handling such a high throughput of writes. [4][9] \n"
    "EXAMPLE TWO: \n"
    "Raw Text: Sources 5 and 7 indicate that the disparity in I/O operations among ranks can be problematic, and the reliance on a single rank can impose significant performance constraints, especially with an environment with 512 processes, and this is despite the application leveraging MPI-IO, which can leverage multiple ranks for enhanced parallelism [9][17]"
    "Corrected Text: The disparity in I/O operations among ranks can be problematic, and the reliance on a single rank can impose significant performance constraints especially with an environment with 512 processes [5][9], and this is despite the application leveraging MPI-IO, which can leverage multiple ranks for enhanced parallelism [9][17]."
)

SOURCE_REFLECTION_EXAMPLES = (
    "EXAMPLE ONE: \n"
    "Analysis summary: The application shows that only one rank is responsible for all I/O operations. This reliance on a single rank can impose significant performance constraints."
    "Source: We perform each run in a separate job allocation to mitigate caching effects. On Lassen, we use one rank per GPU"
    "Answer: no\n"
    "Reasoning: Even though the text says one rank, they are referencing an entirely separate context and are not referencing one rank for the entire application but rather one rank for every GPU allocated to this specific application utilized."
    "EXAMPLE TWO: \n"
    "Analysis summary: The metadata operations for the single rank average 165.90 seconds, which is a considerable amount of time in relation to the overall application runtime"
    "Source: This approach consists of having each process access its own file. This reduces possible interference between the I/O of different processes but increases the number of metadata operations—a problem especially for file systems with a single metadata server, such as Lustre",
    "Answer: yes"
    "Reasoning: This source directly ties into the consequences of having the application spend a significant amount of time conducting metadata operations and its implications on the wider performance of the application"
)

RAG_DIAGNOSIS_FORMAT = (
    "```"
    "### I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior of the application>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Issue 1>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "2. **<Issue 2>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "3. **<Issue 3>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "```\n\n"
    "Here is an example of a diagnosis in the correct format:\n\n"
    "```"
    "### I/O behavior analysis: \n\n"
    " - Both minimum and maximum alignment, along with the mean file alignment size, are 1,048,576 bytes (1 MB)\n\n"
    " - Memory alignment sizes are uniformly 8 bytes, representing typical alignments for data types such as int, double, or pointers\n\n"
    " - The application exhibits a pattern of accessing files with misaligned read and write requests, indicating potential inefficiencies in the I/O strategy being executed by MPI-IO.\n\n"
    "### Diagnosed I/O performance issues: \n\n"
    "1. **Misaligned file access patterns**:\n"
    " - The application exhibits a pattern of accessing files with misaligned read and write requests, indicating potential inefficiencies in the I/O strategy being executed by MPI-IO."
    "Analysis of the trace log data shows that the file alignment size for all 89 file accessed by the application is 1,048,576 bytes (1 MB), but 97%% of the application's read requests "
    "and 85%% of the application's write requests are significantly below 1MB, with the largest read request being 522,259 bytes and the largest write request being 524,288 bytes. "
    "When applications have frequent non-aligned accesses, it might lead to suboptimal performance as unaligned I/O operations can increase overhead and reduce bandwidth.\n\n"
    "2. **Large number of small write requests**:\n"
    "  - The application exhibits a large number of small write requests, which can lead to inefficient use of network bandwidth and increased latency."
    "Analysis of the trace log data shows that the application has 12,345 small write requests, with the largest write request being 128 KB. "
    "This pattern can lead to inefficient use of network bandwidth and increased latency, as the application may be using more time sending small write requests than it would take to send a larger request.\n\n"
    "```\n\n"
    "If there are no issues diagnosed, you should include the I/O behavior analysis and state that no issues are diagnosed as shown in this example:\n\n"
    "```"
    "### I/O behavior analysis: \n\n"
    " - The application exhibits a pattern dominated by 99%% consecutive and sequential access patterns for both read and write requests, meaning offsets are directly adjacent to each other (consecutive) and always increasing (sequential).\n\n"
    " - The application exhibited only 3 read/write switches, indicating the application maintains consistent request patterns.\n\n"
    "### Diagnosed I/O performance issues: \n\n"
    " - The application exhibits consecutive access patterns for both read and write requests, with few read/write switches. This indicates that the application maintains consistent request patterns which are efficient and allow for high throughput and low latency. Thus, there are no major issues currently plaguing this application."
    "```\n\n"
    "Do not add any additional sections to the format."
)

RAG_FREE_DIAGNOSIS_FORMAT = (
    "```"
    "### I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior of the application>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Issue 1>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "2. **<Issue 2>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "3. **<Issue 3>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "```\n\n"
    "Here is an example of a diagnosis in the correct format:\n\n"
    "```"
    "### I/O behavior analysis: \n\n"
    " - Both minimum and maximum alignment, along with the mean file alignment size, are 1,048,576 bytes (1 MB)\n\n"
    " - Memory alignment sizes are uniformly 8 bytes, representing typical alignments for data types such as int, double, or pointers\n\n"
    " - The application exhibits a pattern of accessing files with misaligned read and write requests, indicating potential inefficiencies in the I/O strategy being executed by MPI-IO.\n\n"
    "### Diagnosed I/O performance issues: \n\n"
    "1. **Misaligned file access patterns**:\n"
    " - The application exhibits a pattern of accessing files with misaligned read and write requests, indicating potential inefficiencies in the I/O strategy being executed by MPI-IO."
    "Analysis of the trace log data shows that the file alignment size for all 89 file accessed by the application is 1,048,576 bytes (1 MB), but 97%% of the application's read requests "
    "and 85%% of the application's write requests are significantly below 1MB, with the largest read request being 522,259 bytes and the largest write request being 524,288 bytes.\n\n"
    "2. **Large number of small write requests**:\n"
    "  - The application exhibits a large number of small write requests, which can lead to inefficient use of network bandwidth and increased latency."
    "Analysis of the trace log data shows that the application has 12,345 small write requests, with the largest write request being 128 KB. "
    "This pattern can lead to inefficient use of network bandwidth and increased latency, as the application may be using more time sending small write requests than it would take to send a larger request.\n\n"
    "```\n\n"
    "If there are no apparent issues, you should include the I/O behavior analysis and state that no issues are diagnosed as shown in this example:\n\n"
    "```"
    "### I/O behavior analysis: \n\n"
    " - The application exhibits a pattern dominated by 99%% consecutive and sequential access patterns for both read and write requests, meaning offsets are directly adjacent to each other (consecutive) and always increasing (sequential).\n\n"
    " - The application exhibited only 3 read/write switches, indicating the application maintains consistent request patterns.\n\n"
    "### Diagnosed I/O performance issues: \n\n"
    " - The application exhibits consecutive access patterns for both read and write requests, with few read/write switches. This indicates that the application maintains consistent request patterns which are efficient and allow for high throughput and low latency. Thus there are no majors issues currently plaguing this application."
    "```\n\n"
    "Do not add any additional sections to the format."
)

RAG_INTRA_MODULE_MERGE_FORMAT = (
     "```"
    "### I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior with key metrics and observations>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Merged Issue 1>** \n"
    "  - <Description of issue, evidence for issue from both trace log analysis if applicable, and source(s) that support the issue diagnosis> \n"
    "  - <Recommendations for addressing the issue and sources that support the recommendation, combining the insights from both analyses if possible>\n"
    "2. **<Merged Issue 2>** \n"
    "  - <Description of issue, evidence for issue from both trace log analysis if applicable, and source(s) that support the issue diagnosis> \n"
    "  - <Recommendations for addressing the issue and sources that support the recommendation, combining the insights from both analyses if possible>\n"
    "```\n\n"
    "Here is an abbreviated example of how you should go about merging two documents together: "
    "Analysis One: \n"
     "```\n\n"
    "### I/O behavior analysis: \n\n"
    "The total metadata time of approximately 165.90 seconds, while a considerable fraction of the total runtime of 927 seconds, is uniformly distributed across all 512 ranks, indicating efficient collective handling of metadata without disparities or inefficiencies among processes [2]."
    "### Diagnosed I/O performance issues:"
    "1. Substantial metadata time:"
    "   - The recorded total metadata time of approximately 165.90 seconds, which constitutes a significant portion of the application’s overall runtime, may indicate potential inefficiencies in metadata handling despite the effective use of collective operations. This overhead can impact the overall application performance in scenarios with heavy load or complex data access patterns [7][11]."
     "```\n\n"
    "Analysis Two: \n\n"
     "```\n\n"
    "### I/O behavior analysis: \n\n"
    "The application utilizes a single rank for all I/O operations, with the MPI-IO module accounting for approximately 99.72% of the total application runtime. This indicates that the application is designed to primarily leverage MPI-IO for data transfers, suggesting a potential bottleneck due to the reliance on only one rank handling I/O [9]\n"
    "Metadata handling occupies a considerable amount of time (averaging 165.90 seconds), which may reflect the overhead associated with managing large data volumes [12], particularly given that there are no other ranks contributing to I/O operations.\n"
    "### Diagnosed I/O performance issues:"
    "1. Single Rank I/O Handling:"
    "- The application shows that only one rank is responsible for all I/O operations. This reliance on a single rank can impose significant performance constraints, particularly in a large-scale environment utilizing 512 processes [13]. The analysis demonstrates that this rank accounts for all the data being written and read, highlighting a possible inefficiency in distributing the I/O workload across multiple ranks to enhance parallelism."
    "2. High Metadata Management Time:"
    "   - The metadata operations for the single rank average 165.90 seconds, which is a considerable amount of time in relation to the overall application runtime. This indicates there may be inefficiencies in how metadata is being managed, and given the scale of data being processed, this could become a critical path that affects the overall performance of the application. [7]"
    "```\n\n"
    "Merged Analyses: \n\n"
    "```\n\n"
    "### I/O behavior analysis: \n\n"
    "The application utilizes a single rank for all I/O operations, with the MPI-IO module accounting for approximately 99.72% of the total application runtime. This concentration of I/O operations in one rank indicates a potential bottleneck, hindering parallelism, especially in a large-scale environment using 512 processes [9]."
    "The absence of any synchronization or view requests suggests that the application has a streamlined I/O strategy. However, the average of 165.90 seconds for metadata handling, occupying a considerable fraction of the total runtime of 927 seconds. This time is uniformly distributed across all ranks, indicating effective handling of metadata [2], but also revealing a significant overhead that may affect performance, especially given the large-scale data sizes [12]."
    "### Diagnosed I/O performance issues:"
    "1. Single Rank I/O Handling:"
    "- The reliance on a single rank for I/O operations can lead to significant performance constraints. This setup reflects an inefficiency in distributing the I/O workload across multiple ranks, limiting the potential benefits of parallelism in a 512-process environment [13]."
    "2. Substantial Metadata Management Time:"
    "   - The high average metadata time of approximately 165.90 seconds is concerning, particularly considering it represents a large part of the overall application runtime. This overhead may become a critical path affecting performance due to inefficient metadata processing  [7][11]."
    "```\n\n"
    "Do not add any additional sections to the format."
)

RAG_FREE_INTRA_MODULE_MERGE_FORMAT = (
     "```"
    "### I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior with key metrics and observations>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Merged Issue 1>** \n"
    "  - <Description of issue, evidence for issue from both trace log analysis if applicable> \n"
    "  - <Recommendations for addressing the issue, combining the insights from both analyses if possible>\n"
    "2. **<Merged Issue 2>** \n"
    "  - <Description of issue, evidence for issue from both trace log analysis if applicable> \n"
    "  - <Recommendations for addressing the issue, combining the insights from both analyses if possible>\n"
    "```\n\n"
    "Here is an abbreviated example of how you should go about merging two documents together: "
    "Analysis One: \n"
     "```\n\n"
    "### I/O behavior analysis: \n\n"
    "The total metadata time of approximately 165.90 seconds, while a considerable fraction of the total runtime of 927 seconds, is uniformly distributed across all 512 ranks, indicating efficient collective handling of metadata without disparities or inefficiencies among processes."
    "### Diagnosed I/O performance issues:"
    "1. Substantial metadata time:"
    "   - The recorded total metadata time of approximately 165.90 seconds, which constitutes a significant portion of the application’s overall runtime, may indicate potential inefficiencies in metadata handling despite the effective use of collective operations. This overhead can impact the overall application performance in scenarios with heavy load or complex data access patterns."
     "```\n\n"
    "Analysis Two: \n\n"
     "```\n\n"
    "### I/O behavior analysis: \n\n"
    "The application utilizes a single rank for all I/O operations, with the MPI-IO module accounting for approximately 99.72% of the total application runtime. This indicates that the application is designed to primarily leverage MPI-IO for data transfers, suggesting a potential bottleneck due to the reliance on only one rank handling I/O\n"
    "Metadata handling occupies a considerable amount of time (averaging 165.90 seconds), which may reflect the overhead associated with managing large data volumes, particularly given that there are no other ranks contributing to I/O operations.\n"
    "### Diagnosed I/O performance issues:"
    "1. Single Rank I/O Handling:"
    "- The application shows that only one rank is responsible for all I/O operations. This reliance on a single rank can impose significant performance constraints, particularly in a large-scale environment utilizing 512 processes. The analysis demonstrates that this rank accounts for all the data being written and read, highlighting a possible inefficiency in distributing the I/O workload across multiple ranks to enhance parallelism."
    "2. High Metadata Management Time:"
    "   - The metadata operations for the single rank average 165.90 seconds, which is a considerable amount of time in relation to the overall application runtime. This indicates there may be inefficiencies in how metadata is being managed, and given the scale of data being processed, this could become a critical path that affects the overall performance of the application."
    "```\n\n"
    "Merged Analyses: \n\n"
    "```\n\n"
    "### I/O behavior analysis: \n\n"
    "The application utilizes a single rank for all I/O operations, with the MPI-IO module accounting for approximately 99.72% of the total application runtime. This concentration of I/O operations in one rank indicates a potential bottleneck, hindering parallelism, especially in a large-scale environment using 512 processes."
    "The absence of any synchronization or view requests suggests that the application has a streamlined I/O strategy. While this can enhance performance by reducing bottlenecks, it raises questions about missed opportunities for optimizations through coordinated synchronization."
    "### Diagnosed I/O performance issues:"
    "1. Single Rank I/O Handling:"
    "- The reliance on a single rank for I/O operations can lead to significant performance constraints. This setup reflects an inefficiency in distributing the I/O workload across multiple ranks, limiting the potential benefits of parallelism in a 512-process environment."
    "2. Substantial Metadata Management Time:"
    "   - The high average metadata time of approximately 165.90 seconds is concerning, particularly considering it represents a large part of the overall application runtime. This overhead may become a critical path affecting performance due to inefficient metadata processing."
    "```\n\n"
    "Do not add any additional sections to the format."
)

RAG_INTER_MODULE_MERGE_FORMAT = (
    "```"
    "### Comprehensive I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior with key metrics and observations from both of the modules>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Merged Issue 1>** \n"
    "  - <Description of issue, evidence, and source(s) for issue from both module analyses if applicable> \n"
    "  - <Recommendations for addressing the issue, combining the insights and source information from both analyses if possible>\n"
    "2. **<Merged Issue 2>** \n"
    "  - <Description of issue, evidence, and source(s) for issue from both module analyses if applicable> \n"
    "  - <Recommendations for addressing the issue, combining the insights and source information from both analyses if possible>\n"
    "```\n\n"
    "Here is an abbreviated example of how you should go about merging two documents together: "
    "Analysis One (MPI-IO Example): \n"
     "```\n\n"
    "### MPI-IO I/O behavior analysis: \n\n"
    "A significant concern arises from the excessive focus on independent writes (196,718), accounting for nearly 99.72% of the total application runtime, which creates a potential bottleneck and limits the application's ability to leverage parallelism. Additionally, The application lacks balance in I/O operations, as evidenced by a significantly lower number of independent reads (76,805). This imbalance raises concerns about potential latency and inefficiencies due to the high frequency of small I/O requests [21][25]."
    "### Diagnosed I/O performance issues:"
    "1. Inefficiency from Independent I/O:"
    "   - The heavy reliance on independent writes versus reads may lead to latency and inefficiencies when managing high volumes of small I/O requests, limiting potential gains from parallel I/O [18]."
    "2. Single Rank I/O Handling"
    "   - The dominant use of a single rank for all I/O operations prevents effective utilization of parallelism, marking a significant performance limitation in a multi-process environment [3]."
     "```\n\n"
    "Analysis Two (POSIX Example): \n"
     "```\n\n"
    "### POSIX I/O behavior analysis: \n\n"
    "MPI-IO comprises around 99.7% of total I/O operations, while the POSIX module accounts for only about 0.28%, which is preferred for efficiently managing large distributed data workloads [19][37]. Metadata operations are minimal, taking about 4.66 seconds of the runtime with 32,312 operations, illustrating efficient metadata management. However, high variability in metadata operation times, with peaks up to 4.57 seconds, can be a concern [4]."
    "### Diagnosed I/O performance issues:"
    "1. High Volume of Small and Medium-Sized I/O Requests::"
    "   - The concentration of write requests in the 100 KB to 1 MB range can lead to increased overhead, suggesting inefficiencies and potential latency from numerous smaller requests."
    "2. Significant Proportion of Unaligned File Access:"
    "   - The file check10.nx16384.3d.hdf5 shows about 46.21% of its requests as unaligned (totaling over 131,000), potentially incurring performance penalties due to added overhead [19]."
    "```\n\n"
    "Merged Analyses (POSIX & MPI Combined Together): \n\n"
    "```\n\n"
    "### Comprehensive I/O behavior analysis: \n\n"
    "The application demonstrates a pronounced reliance on MPI-IO, with the module comprising approximately 99.7% of its total I/O operations. This is fitting for parallel I/O management, especially in HPC environments with 512 processes involved [19][37]. Metadata operations were generally efficient, constituting around 4.66 seconds out of 927 total. However, the high variability in metadata operation times (up to 4.57 seconds) flags an overhead concern alongside an absence of collective read and write operations, which could enhance performance by better coordinating access among ranks [4]. Data size management primarily fell in the small to medium range—read operations were mostly in the 100 KB to 1 MB (46.7%) and 1 MB to 4 MB (34.2%) brackets, with write operations also concentrated in the 100 KB to 1 MB (63.6%) range. This pattern suggests effective use of caching and buffering strategies, yet could also indicate potential inefficiencies due to the high number of smaller requests and unaligned accesses, especially notable in files like check10.nx16384.3d.hdf5 [21][25]—a problem especially exacerbated by the utilization of only a single rank [3]"
    "### Diagnosed I/O performance issues:"
    "1. Over-reliance on Independent I/O Operations:"
    "- The significant skew towards independent writes contributes to latency and restricts the benefits of parallel I/O, exacerbating inefficiencies in a large multi-process environment [18]."
    "2. Unaligned Access Overheads:"
    "   - The file check10.nx16384.3d.hdf5 shows about 46.21% of its requests as unaligned (totaling over 131,000), potentially incurring performance penalties due to added overhead [19]"
    "```\n\n"
    "Do not add any additional sections to the format."

)

RAG_FREE_INTER_MODULE_MERGE_FORMAT = (
    "```"
    "### Comprehensive I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior with key metrics and observations from both of the modules>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Merged Issue 1>** \n"
    "  - <Description of issue, evidence for issue from both module analyses if applicable> \n"
    "  - <Recommendations for addressing the issue, combining the insights from both analyses if possible>\n"
    "2. **<Merged Issue 2>** \n"
    "  - <Description of issue, evidence for issue from both module analyses if applicable> \n"
    "  - <Recommendations for addressing the issue, combining the insights from both analyses if possible>\n"
    "```\n\n"
    "Here is an abbreviated example of how you should go about merging two documents together: "
    "Analysis One (MPI-IO Example): \n"
     "```\n\n"
    "### MPI-IO I/O behavior analysis: \n\n"
    "A significant concern arises from the excessive focus on independent writes (196,718), accounting for nearly 99.72% of the total application runtime, which creates a potential bottleneck and limits the application's ability to leverage parallelism. Additionally, The application lacks balance in I/O operations, as evidenced by a significantly lower number of independent reads (76,805). This imbalance raises concerns about potential latency and inefficiencies due to the high frequency of small I/O requests."
    "### Diagnosed I/O performance issues:"
    "1. Inefficiency from Independent I/O:"
    "   - The heavy reliance on independent writes versus reads may lead to latency and inefficiencies when managing high volumes of small I/O requests, limiting potential gains from parallel I/O."
    "2. Single Rank I/O Handling"
    "   - The dominant use of a single rank for all I/O operations prevents effective utilization of parallelism, marking a significant performance limitation in a multi-process environment."
     "```\n\n"
    "Analysis Two (POSIX Example): \n"
     "```\n\n"
    "### POSIX I/O behavior analysis: \n\n"
    "MPI-IO comprises around 99.7% of total I/O operations, while the POSIX module accounts for only about 0.28%, which is preferred for efficiently managing large distributed data workloads. Metadata operations are minimal, taking about 4.66 seconds of the runtime with 32,312 operations, illustrating efficient metadata management. However, high variability in metadata operation times, with peaks up to 4.57 seconds, can be a concern."
    "### Diagnosed I/O performance issues:"
    "1. High Volume of Small and Medium-Sized I/O Requests::"
    "   - The concentration of write requests in the 100 KB to 1 MB range can lead to increased overhead, suggesting inefficiencies and potential latency from numerous smaller requests."
    "2. Significant Proportion of Unaligned File Access:"
    "   - The file check10.nx16384.3d.hdf5 shows about 46.21% of its requests as unaligned (totaling over 131,000), potentially incurring performance penalties due to added overhead."
    "```\n\n"
    "Merged Analyses (POSIX & MPI Combined Together): \n\n"
    "```\n\n"
    "### Comprehensive I/O behavior analysis: \n\n"
    "The application demonstrates a pronounced reliance on MPI-IO, with the module comprising approximately 99.7% of its total I/O operations. This is fitting for parallel I/O management, especially in HPC environments with 512 processes involved. Metadata operations were generally efficient, constituting around 4.66 seconds out of 927 total. However, the high variability in metadata operation times (up to 4.57 seconds) flags an overhead concern alongside an absence of collective read and write operations, which could enhance performance by better coordinating access among ranks. Data size management primarily fell in the small to medium range—read operations were mostly in the 100 KB to 1 MB (46.7%) and 1 MB to 4 MB (34.2%) brackets, with write operations also concentrated in the 100 KB to 1 MB (63.6%) range. This pattern suggests effective use of caching and buffering strategies, yet could also indicate potential inefficiencies due to the high number of smaller requests and unaligned accesses, especially notable in files like check10.nx16384.3d.hdf5"
    "### Diagnosed I/O performance issues:"
    "1. Over-reliance on Independent I/O Operations:"
    "- The significant skew towards independent writes contributes to latency and restricts the benefits of parallel I/O, exacerbating inefficiencies in a large multi-process environment."
    "2. Unaligned Access Overheads:"
    "   - The file check10.nx16384.3d.hdf5 shows about 46.21% of its requests as unaligned (totaling over 131,000), potentially incurring performance penalties due to added overhead"
    "```\n\n"
    "Do not add any additional sections to the format."

)

FINAL_DIAGNOSIS_FORMAT = (
    "```"
    "### I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior with key metrics and observations>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Issue 1>** \n"
    "  - <Description of issue, evidence for issue from the trace log analysis, and source(s) that support the issue diagnosis> \n"
    "  - <Recommendations for addressing the issue and sources that support the recommendation>\n"
    "2. **<Issue 2>** \n"
    "  - <Description of issue, evidence for issue from the trace log analysis, and source(s) that support the issue diagnosis> \n"
    "  - <Recommendations for addressing the issue and sources that support the recommendation>\n"
    "```\n\n"
)

FINAL_RAG_FREE_DIAGNOSIS_FORMAT = (
    "```"
    "### I/O behavior analysis: \n\n"
    "<Summary description of important I/O behavior with key metrics and observations>\n\n"
    "### Diagnosed I/O performance issues: \n"
    "1. **<Issue 1>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "  - <Recommendations for addressing the issue>\n"
    "2. **<Issue 2>** \n"
    "  - <Description of issue and evidence for issue from the trace log analysis> \n"
    "  - <Recommendations for addressing the issue and sources that support the recommendation>\n"
    "```\n\n"
)


'''
Depending on the model specified, LiteLLM handles much of the prompt formatting for us depending on the model specified (notably it supports Llama and Mistral): https://github.com/BerriAI/litellm/blob/main/litellm/litellm_core_utils/prompt_templates/factory.py
'''
prompt_templates = {
    "code_interpretation": {
        "system_context": {"prompt": 
                                "You are an expert in code interpretation. You will be given snippets of code "
                                "and must describe what they are intended to do. Specifically the snippets of code "
                                "will be part of an analysis and data extraction process of HPC application trace logs collected using Darshan I/O Profiler. "
                                "Be sure to keep the descriptions to the point and only contain relevant information while still maintaining a high level of accuracy and detail.",
                            "kwargs": []},
        "user_prompt": {"prompt": 
                                "Given the following code snippet, give a brief, 2-5 sentence interpretation of what the code is doing: \n\n{code} ",
                        "kwargs": ["code"]}
    },
    "summary_to_info": {
        "system_context": {"prompt": 
                                "You will be given a code description, a code snippet, and the return value for the code. "
                                "The snippets of code will be part of an analysis process of HPC application trace logs collected using Darshan."
                                "You will also be given some context of the application trace as a whole, beyond just the {module} "
                                "information to provide context for the scale and scope of the application. "
                                "While later analysis will investigate other modules in more detail, note that this "
                                "part of the analysis only looks at one portion of the {module} Darshan module data extracted from the trace log. "
                                "Your task is to give a precise and accurate interpretation of the output values in the context "
                                "of what was analyzed and the larger view of the application without suggesting any improvements or "
                                "potential problems.  "
                                "It is crucial that your judgments of scale are guided by overall application context provided."
                                f"{DARSHAN_HELPFUL_CONTEXT}"
                                "Be sure to keep your responses concise and to the point.",
                            "kwargs": ["module"]},
        "user_prompt": {"prompt":
                                "Given the following code description, code snippet, and code output analyzing a specific aspect of "
                                "I/O trace data from just the {module} module, provide an interpretation of the output in the context "
                                "of what was analyzed and the larger view of the application without suggesting any improvements or "
                                "potential problems: \n\n "
                                "Here is the analysis: \n{summary} \n\n "
                                "Here is the broader context of the application trace: \n{trace_context}",
                        "kwargs": ["module", "summary", "trace_context"]
        },
    },
    "rag_diagnosis": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "A user has run a process to extract key summary information from a Darshan trace log. "
                                "You will be given a detailed description of the summary information along with a number of sources extracted from research papers which may be related to interpreting the summary information. \n\n"
                                " ## Your Task: \n"
                                " - Use your expertise as well as the provided sources to determine whether the summary information indicates any potential I/O performance issues.\n\n"
                                " ## Additional Instructions and Information: \n"
                                " - Your diagnosis should only be based on factual information provided in the summary and sources. \n"
                                " - Your analysis should be detailed and include all important information"
                                " - Do not recommend further analyses.\n"
                                " - Do not provide inline citations in your response and do not mention specific source IDs in your response. \n"
                                " - You must always respond in proper JSON format and the diagnosis should be structured using Markdown syntax. \n\n "
                                " ## Useful Darshan Context: \n"
                                f"{DARSHAN_HELPFUL_CONTEXT}\n\n",
                            "kwargs": []},
        "user_prompt": {"prompt":
                                "Here is an analysis summary of the trace log: \n{description} "
                                "Here are the sources that were utilized to generate this analysis: \n{sources}",
                            "kwargs": ["description", "sources"],
                            "response_format": RAGDiagnosis
                    }
    },
    "rag_free_diagnosis": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "A user has run a process to extract key summary information from a Darshan trace log. "
                                "You will be given an analysis summary investigating an aspect of the trace log. "
                                "Your task is to: \n"
                                "1. Provide context regarding the I/O behavior of the application.\n"
                                "2. Determine whether the summary information indicates any I/O performance issues.\n"
                                "3. Ensure all information is useful to the diagnosis.\n"
                                "4. Do not recommend further analyses.\n\n"
                                "Your diagnosis should follow this format: \n"
                                f"{RAG_FREE_DIAGNOSIS_FORMAT}",
                            "kwargs": ["description"]
                            },
        "user_prompt": {"prompt":
                                "Here is the analysis summary of the trace log: \n{description}",
                        "kwargs": ["description"]}
    },
    "intra_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "I have conducted an analysis of various aspects of an HPC application I/O trace log collected using Darshan. "
                                "You will be given two analysis summaries investigating two different aspects of the trace log pertaining only to the {module} module.\n\n"
                                " ## Your task: \n"
                                " - Create a new, more comprehensive summary based on the two provided summaries.\n"
                                " - Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                " - Highlight any potential I/O performance issues found in either analysis.\n"
                                " - Do not forget to include any important information from the provided analysis summaries.\n\n"
                                " ## Additional Instructions and Information: \n"
                                " - Your combined diagnosis should only be based on factual information provided by the two provided analysis summaries and sources. \n"
                                " - Do not recommend further analyses.\n"
                                " - Do not provide inline citations in your response and do not mention specific source IDs in your response. \n"
                                " - You must always respond in proper JSON format and the diagnosis should be structured using Markdown syntax. \n"
                                "## Useful Darshan Context: \n"
                                f"{DARSHAN_HELPFUL_CONTEXT}\n\n"
                                "Also note that the new merged summary will not be a comprehensive evaluation of the {module} module, as other aspects will be merged separately.",
                            "kwargs": ["module"]},
        "user_prompt": {"prompt":
                                "Create a new summary based on the following two performance analyses of two different aspects of the {module} module: \n"
                                "## Analysis 1: \n"
                                "{fragment1_diagnosis} \n"
                                "## Analysis 2: \n"
                                "{fragment2_diagnosis} \n"
                                "## Sources: \n"
                                "{sources} \n\n",
                            "kwargs": ["module", "fragment1_diagnosis", "fragment2_diagnosis", "sources"],
                            "response_format": RAGDiagnosis}
    },
    "rag_free_intra_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "I have conducted an analysis of various aspects of an HPC application I/O trace log collected using Darshan. "
                                "You will be given two analysis summaries investigating two different aspects of the trace log pertaining only to the {module} module."
                                "Your task is to: \n"
                                "1. Create a new, more comprehensive summary based on the two provided summaries.\n"
                                "2. Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                "3. Highlight any potential I/O performance issues found in either analysis.\n"
                                "4. Do not forget any important information from the provided analysis summaries.\n\n"
                                f"{DARSHAN_HELPFUL_CONTEXT}"
                                "Also note that the new merged summary will not be a comprehensive evaluation of the {module} module, as other aspects will be merged separately."
                                "Utilize the following format when conducting your merge:\n"
                                f"{RAG_FREE_INTRA_MODULE_MERGE_FORMAT}",
                            "kwargs": ["module"]},
        "user_prompt": {"prompt":
                                "Create a new summary based on the following two performance analyses of two different aspects of the {module} module: \n"
                                "Analysis 1: \n{fragment1_diagnosis} \n\n"
                                "Analysis 2: \n{fragment2_diagnosis} \n\n"
                                "New merged summary:",
                            "kwargs": ["module", "fragment1_diagnosis", "fragment2_diagnosis"]}
    },
    "final_intra_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "I have conducted an analysis of various aspects of an HPC application I/O trace log collected using Darshan. "
                                "You will be given two analysis summaries investigating two different aspects of the trace log pertaining only to the {module} module.\n\n"
                                " ## Your task: \n"
                                " - Create a new, more comprehensive summary based on the two provided summaries.\n"
                                " - Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                " - Highlight any potential I/O performance issues found in either analysis.\n"
                                " - Do not forget to include any important information from the provided analysis summaries.\n\n"
                                " ## Additional Instructions and Information: \n"
                                " - Your combined diagnosis should only be based on factual information provided by the two provided analysis summaries and sources. \n"
                                " - Do not recommend further analyses.\n"
                                " - Do not provide inline citations in your response and do not mention specific source IDs in your response. \n"
                                " - You must always respond in proper JSON format and the diagnosis should be structured using Markdown syntax. \n"
                                " ## Useful Darshan Context: \n"
                                f"{DARSHAN_HELPFUL_CONTEXT}\n\n"
                                "Also note that the new merged summary should be a comprehensive evaluation of the {module} module.",
                            "kwargs": ["module"]},
        "user_prompt": {"prompt":
                                "Create a comprehensive analysis summary of the {module} module based on the following two performance analysis summaries: \n"
                                "## Analysis 1: \n"
                                "{fragment1_diagnosis} \n\n"
                                "## Analysis 2: \n"
                                "{fragment2_diagnosis} \n\n"
                                "## Sources: \n"
                                "{sources} \n\n",
                            "kwargs": ["module", "fragment1_diagnosis", "fragment2_diagnosis", "sources"],
                            "response_format": RAGDiagnosis}
    },
    "final_rag_free_intra_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "I have conducted an analysis of various aspects of an HPC application I/O trace log collected using Darshan. "
                                "You will be given two analysis summaries investigating two different aspects of the trace log pertaining only to the {module} module."
                                "Your task is to: \n"
                                "1. Create a new, more comprehensive summary based on the two provided summaries.\n"
                                "2. Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                "3. Highlight any potential I/O performance issues found in either analysis.\n"
                                "4. Do not forget any important information from the provided analysis summaries.\n\n"
                                f"{DARSHAN_HELPFUL_CONTEXT}"
                                "Also note that the new merged summary should be a comprehensive evaluation of the {module} module."
                                "Utilize the following format when conducting your merge:\n"
                                f"{RAG_FREE_INTRA_MODULE_MERGE_FORMAT}",
                            "kwargs": ["module"]},
        "user_prompt": {"prompt":
                                "Create a comprehensive analysis summary of the {module} module based on the following two performance analysis summaries: \n"
                                "Analysis 1: \n{fragment1_diagnosis} \n\n"
                                "Analysis 2: \n{fragment2_diagnosis} \n\n"
                                "New merged analysis: ",
                            "kwargs": ["module", "fragment1_diagnosis", "fragment2_diagnosis"]}
    },
    "inter_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "You will be given two analysis summaries investigating different aspects of the trace log pertaining to various Darshan modules.\n\n"
                                " ## Your task: \n"
                                " - Create a new, more comprehensive summary based on the two provided summaries.\n"
                                " - Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                " - Highlight any potential I/O performance issues found in either analysis.\n"
                                " - Do not forget to include any important information from the provided analysis summaries.\n\n"
                                " ## Additional Instructions and Information: \n"
                                " - Your combined diagnosis should only be based on factual information provided by the two provided analysis summaries and sources. \n"
                                " - Do not recommend further analyses.\n"
                                " - Do not provide inline citations in your response and do not mention specific source IDs in your response. \n"
                                " - You must always respond in proper JSON format and the diagnosis should be structured using Markdown syntax. \n"
                                " ## Useful Darshan Context: \n"
                                f"{DARSHAN_HELPFUL_CONTEXT}\n\n"
                                "Also note that the new merged summary should consider and combine the information from all of the modules analyzed.",
                            "kwargs": []
        },
        "user_prompt": {"prompt": 
                                "Create a diagnosis that combines the information from the following two summaries containing information from these modules: "
                                "{all_modules}.\n\n"
                                "## Analysis 1: \n"
                                "{fragment1_diagnosis} \n\n"
                                "## Analysis 2: \n"
                                "{fragment2_diagnosis} \n\n"
                                "## Sources: \n"
                                "{sources} \n\n",
                            "kwargs": ["all_modules", "fragment1_diagnosis", "fragment2_diagnosis", "sources"],
                            "response_format": RAGDiagnosis}
    },
    "rag_free_inter_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "You will be given two analysis summaries investigating different aspects of the trace log pertaining to various Darshan modules."
                                "Your task is to: \n"
                                "1. Create a new, more comprehensive summary based on the two provided summaries.\n"
                                "2. Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                "3. Highlight any potential I/O performance issues found in the analysis summary.\n"
                                "4. Do not forget any important information from either the provided analysis summaries!\n\n"
                                f"{DARSHAN_HELPFUL_CONTEXT}"
                                "Also note that the new merged summary should consider and combine the information from all of the modules analyzed."
                                "Use the following format and example to guide your merging process:"
                                f"{RAG_FREE_INTER_MODULE_MERGE_FORMAT} ",
                            "kwargs": []
        },
        "user_prompt": {"prompt": 
                                "Create a diagnosis that combines the information from the following two summaries containing information from these modules: "
                                "{all_modules}.\n\n"
                                "Analysis 1:\n{fragment1_diagnosis}\n\n"
                                "Analysis 2:\n{fragment2_diagnosis}\n\n"
                                "New merged analysis: ",
                            "kwargs": ["all_modules", "fragment1_diagnosis", "fragment2_diagnosis"]
        }
    },
    "final_inter_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "You will be given two analysis summaries investigating different aspects of the trace log pertaining to various Darshan modules.\n\n"
                                " ## Your task: \n"
                                " - Create a new, more comprehensive summary based on the two provided summaries.\n"
                                " - Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                " - Highlight any potential I/O performance issues found in either analysis.\n"
                                " - Do not forget to include any important information from the provided analysis summaries.\n\n"
                                " ## Additional Instructions and Information: \n"
                                " - Your combined diagnosis should only be based on factual information provided by the two provided analysis summaries and sources. \n"
                                " - Do not recommend further analyses.\n"
                                " - Do not provide inline citations in your response and do not mention specific source IDs in your response. \n"
                                " - You must always respond in proper JSON format and the diagnosis should be structured using Markdown syntax. \n"
                                " ## Useful Darshan Context: \n"
                                f"{DARSHAN_HELPFUL_CONTEXT}\n\n",
                            "kwargs": []
        },
        "user_prompt": {"prompt": 
                                "Create a diagnosis that combines the information from the following two summaries containing information from these modules: "
                                "{all_modules}.\n\n"
                                "## Analysis 1: \n"
                                "{fragment1_diagnosis} \n\n"
                                "## Analysis 2: \n"
                                "{fragment2_diagnosis} \n\n"
                                "## Sources: \n"
                                "{sources} \n\n",
                            "kwargs": ["all_modules", "fragment1_diagnosis", "fragment2_diagnosis", "sources"],
                            "response_format": RAGDiagnosis
        }
    },
    "final_rag_free_inter_module_merge": {
        "system_context": {"prompt": 
                                "You are an expert in HPC I/O performance diagnosis. "
                                "You will be given two analysis summaries investigating different aspects of the trace log pertaining to various Darshan modules."
                                "Your task is to: \n"
                                "1. Create a new, more comprehensive summary for the user's application based on the two provided summaries.\n"
                                "2. Remove redundant information and resolve any contradictions between the analyses but keep all relevant information.\n"
                                "3. Highlight any potential I/O performance issues found in the analysis summary.\n"
                                "4. Do not forget any important information from the provided analysis summaries.\n\n"
                                "Note that the new merged summary should be a comprehensive evaluation of the application."
                                f"{DARSHAN_HELPFUL_CONTEXT}"
                                "Your analysis should adhere to the following format: \n"
                                f"{FINAL_DIAGNOSIS_FORMAT}"                                
                                "Use the following format and example to guide your merging process:"
                                f"{RAG_FREE_INTER_MODULE_MERGE_FORMAT}",
                            "kwargs": []
        },
        "user_prompt": {"prompt": 
                                "Create a diagnosis that combines the information from the following two summaries containing information from these modules: "
                                "{all_modules}.\n\n"
                                "Analysis 1:\n{fragment1_diagnosis}\n\n"
                                "Analysis 2:\n{fragment2_diagnosis}\n\n"
                                "New merged analysis: ",
                            "kwargs": ["all_modules", "fragment1_diagnosis", "fragment2_diagnosis"]
        }
    },
    "format_markdown": {
        "system_context": {"prompt": 
                                "user The user has conducted an analysis of various aspects of an HPC application I/O trace log collected using Darshan."
                                "You will be provided with a summary of the analysis results from a Darshan module. "
                                "Your task is to format the summary into a markdown document. "
                                "The markdown document should be formatted in a way that is easy to read and understand. "
                                "The document should be formatted in a way that highlights the key information and insights provided in the summary. ",
                            "kwargs": []
        },
        "user_prompt": {"prompt": 
                                "user The following is the summary of the analysis results from a Darshan module:\n{diagnosis}\n\n"
                                "Please format the summary into a markdown document. ",
                            "kwargs": ["diagnosis"]
        }
    }
    
}

PROMPT_TYPES = list(prompt_templates.keys())

def preprocess_all_modules_to_txt(all_modules):
    all_modules_list = []
    for module in all_modules:
        if '_' in module:
            module_name = module.split("_")[0]
            all_modules_list.append(module_name)
        else:
            all_modules_list.append(module)
    return ", ".join(all_modules_list[:-1]) + " and " + all_modules_list[-1]


def get_all_kwargs(prompt_type):
    prompt_template = prompt_templates[prompt_type]
    if "system_context" in prompt_template:
        return set(prompt_template["system_context"]["kwargs"] + prompt_template["user_prompt"]["kwargs"])
    else:
        return set(prompt_template["user_prompt"]["kwargs"])

def format_simple_prompt(prompt_type, kwargs):
    prompt_template = prompt_templates[prompt_type]
    all_kwargs = get_all_kwargs(prompt_type)
    if "sources" in kwargs:
        kwargs["sources"] = json.dumps(kwargs["sources"], indent=4)
    if len(kwargs) != len(all_kwargs):
        raise ValueError(f"Expected {len(all_kwargs)} kwargs, but got {len(kwargs)}")
    if "system_context" in prompt_template:
        system_context = prompt_template["system_context"]["prompt"].format(**kwargs)
    else:
        system_context = None
    user_prompt = prompt_template["user_prompt"]["prompt"].format(**kwargs)
    if "response_format" in prompt_template["user_prompt"]:
        user_prompt += "\n\n" + "Your response must follow this specific JSON structure: \n" + json.dumps(prompt_template["user_prompt"]["response_format"].model_json_schema(), indent=4)
        user_prompt += "\n\n" + "Remember not to provide inline citations in your response and do not mention specific source IDs in the response. Only list the source IDs in the sources field of the JSON response."

    if system_context is None:
        return [{"role": "user", "content": user_prompt}]
    else:
        return [{"role": "system", "content": system_context}, {"role": "user", "content": user_prompt}]


def deduplicate_sources(sources1, sources2):
    # sources1 and sources2 are dictionaries with source IDs as keys and source information as values; source information is a dictionary with a "file" key and a "text" key
    # create a new dictionary with the union of the two dictionaries
    # if a source ID is present in both dictionaries, keep only one instance of it
    # return the new dictionary with ordered source IDs
    new_sources = []
    for source_id in sources1:
        source_tuple = (sources1[source_id]["file"], sources1[source_id]["text"])
        if source_tuple not in new_sources:
            new_sources.append(source_tuple)
    for source_id in sources2:
        source_tuple = (sources2[source_id]["file"], sources2[source_id]["text"])
        if source_tuple not in new_sources:
            new_sources.append(source_tuple)

    new_source_dict = {}
    for idx, source in enumerate(new_sources):
        new_source_dict[f"Source {idx+1}"] = {"file": source[0], "text": source[1]}
    return new_source_dict

def format_merge_prompt(prompt_type, fragment1, fragment2, kwargs):
    fragment1_diagnosis = fragment1["diagnosis"]
    fragment2_diagnosis = fragment2["diagnosis"]
    kwargs["fragment1_diagnosis"] = fragment1_diagnosis
    kwargs["fragment2_diagnosis"] = fragment2_diagnosis
    if not "rag_free" in prompt_type:
        sources = deduplicate_sources(fragment1["sources"], fragment2["sources"])
        kwargs["sources"] = sources
    else:
        sources = {}

    if "all_modules" in kwargs:
        kwargs["all_modules"] = preprocess_all_modules_to_txt(kwargs["all_modules"])

    return format_simple_prompt(prompt_type, kwargs), sources
        

    

