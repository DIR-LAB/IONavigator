import os
import pandas as pd
import json
import inspect
import re



################################################################
########################## Helper Functions ##########################
################################################################

def get_darshan_modules(trace_path):
    # look for all csv files in the directory
    header = None
    modules = {}
    for filename in os.listdir(trace_path):
        if filename.endswith('.csv'):
            module_name = filename.split('.')[0]
            modules[module_name] = pd.read_csv(os.path.join(trace_path, filename))
            # convert all columns with spaces to underscores
            modules[module_name].columns = modules[module_name].columns.str.replace(' ', '_')
        elif filename.endswith('.json'):
            with open(os.path.join(trace_path, filename), 'r') as f:
                header = json.load(f)
    return modules, header


def extract_single_method_code(source_code, start_pos):
    """Extracts the full method code starting from the given position."""
    # Look for the next 'def' or end of class
    end_pos = source_code.find('def ', start_pos + 1)
    if end_pos == -1:
        end_pos = len(source_code)
    method_code = source_code[start_pos:end_pos].strip()
    return method_code

def extract_class_methods(cls):
    methods = []
    
    # Get the source code of the entire class
    source_code = inspect.getsource(cls)
    
    # Use regex to find all method definitions
    method_pattern = re.compile(r'def\s+(\w+)\s*\(.*?\):')
    matches = method_pattern.finditer(source_code)
    
    # Extract each method's code based on the regex matches
    for match in matches:
        method_name = match.group(1)
        method_code = extract_single_method_code(source_code, match.start())
        methods.append(method_code)
    
    return methods

def process_trace_header(header):
    if type(header) == list and len(header) == 1:
        header = header[0]
    elif type(header) == list and len(header) > 1:
        min_start_time = min([int(item['start']) for item in header])
        max_end_time = max([int(item['end']) for item in header])
        runtime = max_end_time - min_start_time
        nprocs = sum([int(item['nprocs']) for item in header])
        header = {"runtime": runtime, "nprocs": nprocs}

    return header


################################################################
########################## Trace Header Extraction ##########################
################################################################

def summarize_trace_header(header, size_summaries):
    summary_info = {}
    summary_info['total application runtime'] = header['runtime']
    summary_info['total number of processes'] = header['nprocs']
    processing_modules = ['POSIX', 'MPI-IO', 'STDIO']
    
    total_size = sum([size_summaries[module]["total_size"] for module in size_summaries])
    if "MPI-IO" in size_summaries:
        # remove the size of MPI-IO from the total size to avoid double counting since MPI-IO is reported also as POSIX
        total_size -= size_summaries["MPI-IO"]["total_size"]
        posix_size = size_summaries["POSIX"]["total_size"] - size_summaries["MPI-IO"]["total_size"]
    elif "POSIX" in size_summaries:
        posix_size = size_summaries["POSIX"]["total_size"]
    else:
        posix_size = 0
    summary_info["proportion of size per module"] = {}
    for module in size_summaries:
        processing_modules.remove(module)
        if module != "POSIX":
            summary_info[f"proportion of size per module"][module] = size_summaries[module]["total_size"]/total_size
        else:
            summary_info[f"proportion of size per module"][module] = posix_size/total_size
    if len(processing_modules) > 0:
        # fill in the rest of the modules with 0
        for module in processing_modules:
            summary_info[f"proportion of size per module"][module] = 0
    return summary_info


###################################################################
########################## Darshan Modules ##########################
###################################################################

class STDIO:
    def __init__(self, stdio_df):
        self.stdio_df = stdio_df
        self.darshan_module = "STDIO"

    def get_size_summary(self):
        self.size_summary = {
            "total_bytes_written": self.stdio_df['STDIO_BYTES_WRITTEN'].sum(),
            "total_bytes_read": self.stdio_df['STDIO_BYTES_READ'].sum(),
            "total_size": self.stdio_df['STDIO_BYTES_WRITTEN'].sum() + self.stdio_df['STDIO_BYTES_READ'].sum()
        }
        return self.size_summary

    
    def get_request_summary(self):
        total_requests = 0
        total_reads = self.stdio_df['STDIO_READS'].sum()
        if total_reads >= 0:
            total_requests += total_reads
        else:
            total_reads = -1
        total_writes = self.stdio_df['STDIO_WRITES'].sum()
        if total_writes >= 0:
            total_requests += total_writes
        else:
            total_writes = -1
        total_opens = self.stdio_df['STDIO_FDOPENS'].sum()
        if total_opens >= 0:
            total_requests += total_opens
        else:
            total_opens = -1
        total_flushes = self.stdio_df['STDIO_FLUSHES'].sum()
        if total_flushes >= 0:
            total_requests += total_flushes
        else:
            total_flushes = -1
        total_seeks = self.stdio_df['STDIO_SEEKS'].sum()
        if total_seeks >= 0:
            total_requests += total_seeks
        else:
            total_seeks = -1
        self.request_summary = {
            "total requests": total_requests,
            "total reads": total_reads,
            "total writes": total_writes,
            "total opens": total_opens,
            "total flushes": total_flushes,
            "total seeks": total_seeks
        }  
        return self.request_summary

    def get_file_summary(self):
        self.file_summary = {}
        # get the top 10 files by size written
        top_files_write = self.stdio_df[["file_name", "STDIO_BYTES_WRITTEN"]].groupby("file_name").sum()
        top_files_write = top_files_write[top_files_write["STDIO_BYTES_WRITTEN"] > 0].sort_values("STDIO_BYTES_WRITTEN", ascending=False).head(10)
        self.file_summary["top_files_write"] = top_files_write.to_dict()
        # get the top 10 files by size read
        top_files_read = self.stdio_df[["file_name", "STDIO_BYTES_READ"]].groupby("file_name").sum()
        top_files_read = top_files_read[top_files_read["STDIO_BYTES_READ"] > 0].sort_values("STDIO_BYTES_READ", ascending=False).head(10)
        self.file_summary["top_files_read"] = top_files_read.to_dict()
        # get the top 10 files by number of non-metadata requests
        top_files_req = self.stdio_df[["file_name", "STDIO_READS", "STDIO_WRITES"]].groupby("file_name").sum()
        top_files_req["total_requests"] = top_files_req["STDIO_READS"] + top_files_req["STDIO_WRITES"]
        top_files_req = top_files_req[top_files_req["total_requests"] > 0].sort_values("total_requests", ascending=False).head(10)
        self.file_summary["top_files_req"] = top_files_req.to_dict()
        # get the top 10 files by number of metadata requests
        top_files_meta = self.stdio_df[["file_name", "STDIO_FDOPENS", "STDIO_FLUSHES", "STDIO_SEEKS"]].groupby("file_name").sum()
        top_files_meta["total_metadata"] = top_files_meta["STDIO_FDOPENS"] + top_files_meta["STDIO_FLUSHES"] + top_files_meta["STDIO_SEEKS"]
        top_files_meta = top_files_meta[top_files_meta["total_metadata"] > 0].sort_values("total_metadata", ascending=False).head(10)
        self.file_summary["top_files_meta"] = top_files_meta.to_dict()
        
        self.file_summary["unique_files"] = len(self.stdio_df["record_id"].unique())
        # UNKNOWN fs means that it is logging to <STDOUT> or <STDERR>
        self.file_summary["unique_files_by_fs"] = self.stdio_df.groupby("fs_type")["file_name"].nunique().to_dict()
        files_by_rank = self.stdio_df.groupby("rank")["file_name"].nunique()
        self.file_summary["mean_unique_files_by_rank"] = files_by_rank.mean()
        self.file_summary["min_unique_files_by_rank"] = files_by_rank.min()
        self.file_summary["max_unique_files_by_rank"] = files_by_rank.max()
        self.file_summary["std_unique_files_by_rank"] = files_by_rank.std()
        self.file_summary["median_unique_files_by_rank"] = files_by_rank.median()
        self.file_summary["top_5_ranks_by_unique_files"] = files_by_rank.sort_values(ascending=False).head(5).to_dict()
        self.file_summary["bottom_5_ranks_by_unique_files"] = files_by_rank.sort_values(ascending=True).head(5).to_dict()
        
        return self.file_summary
    
    def summarize(self):
        self.get_size_summary()
        self.get_request_summary()
        self.get_file_summary()
        return self.size_summary, self.request_summary, self.file_summary


class POSIX:
    def __init__(self, posix_df):
        self.posix_df = posix_df
        self.darshan_module = "POSIX"

    def get_size_summary(self):
        posix_reads = self.posix_df['POSIX_READS'].sum()
        posix_writes = self.posix_df['POSIX_WRITES'].sum()
        total_requests = posix_reads + posix_writes
        # get top 4 access sizes and counts for the 5 files with the most requests
        top_files = self.posix_df[["file_name", "POSIX_READS", "POSIX_WRITES"]].groupby("file_name").sum()
        top_files["total_requests"] = top_files[["POSIX_READS", "POSIX_WRITES"]].sum(axis=1)
        top_files = top_files[top_files["total_requests"] > 0].sort_values("total_requests", ascending=False).head(5)
        top_files = self.posix_df.loc[self.posix_df["file_name"].isin(top_files.index)]
        top_sizes_dict = {}
        for i in range(4):
            size_key = f"POSIX_ACCESS{i+1}_ACCESS"
            count_key = f"POSIX_ACCESS{i+1}_COUNT"
            top_sizes_dict[f"size_{i+1}"] = dict(zip(top_files["file_name"], top_files[size_key]))
            if total_requests > 0:
                top_sizes_dict[f"count_{i+1}"] = dict(zip(top_files["file_name"], top_files[count_key]/total_requests))
            else:
                top_sizes_dict[f"count_{i+1}"] = dict(zip(top_files["file_name"], top_files[count_key]))


        if posix_reads > 0:
            read_hist = {
                "0-100": (self.posix_df["POSIX_SIZE_READ_0_100"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "100-1k": (self.posix_df["POSIX_SIZE_READ_100_1K"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "1k-10k": (self.posix_df["POSIX_SIZE_READ_1K_10K"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "10k-100k": (self.posix_df["POSIX_SIZE_READ_10K_100K"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "100k-1M": (self.posix_df["POSIX_SIZE_READ_100K_1M"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "1M-4M": (self.posix_df["POSIX_SIZE_READ_1M_4M"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "4M-10M": (self.posix_df["POSIX_SIZE_READ_4M_10M"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "10M-100M": (self.posix_df["POSIX_SIZE_READ_10M_100M"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "100M-1G": (self.posix_df["POSIX_SIZE_READ_100M_1G"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float),
                "1G+": (self.posix_df["POSIX_SIZE_READ_1G_PLUS"].sum() / self.posix_df['POSIX_READS'].sum()).astype(float)
            }
        else:
            read_hist = {
                "0-100": 0,
                "100-1k": 0,
                "1k-10k": 0,
                "10k-100k": 0,
                "100k-1M": 0,
                "1M-4M": 0,
                "4M-10M": 0,
                "10M-100M": 0,
                "100M-1G": 0,
                "1G+": 0
            }
        if posix_writes > 0:
            write_hist = {
                "0-100": (self.posix_df["POSIX_SIZE_WRITE_0_100"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "100-1k": (self.posix_df["POSIX_SIZE_WRITE_100_1K"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "1k-10k": (self.posix_df["POSIX_SIZE_WRITE_1K_10K"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "10k-100k": (self.posix_df["POSIX_SIZE_WRITE_10K_100K"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "100k-1M": (self.posix_df["POSIX_SIZE_WRITE_100K_1M"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "1M-4M": (self.posix_df["POSIX_SIZE_WRITE_1M_4M"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "4M-10M": (self.posix_df["POSIX_SIZE_WRITE_4M_10M"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "10M-100M": (self.posix_df["POSIX_SIZE_WRITE_10M_100M"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "100M-1G": (self.posix_df["POSIX_SIZE_WRITE_100M_1G"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float),
                "1G+": (self.posix_df["POSIX_SIZE_WRITE_1G_PLUS"].sum() / self.posix_df['POSIX_WRITES'].sum()).astype(float)
            }
        else:
            write_hist = {
                "0-100": 0,
                "100-1k": 0,
                "1k-10k": 0,
                "10k-100k": 0,
                "100k-1M": 0,
                "1M-4M": 0,
                "4M-10M": 0,
                "10M-100M": 0,
                "100M-1G": 0,
                "1G+": 0
            }
        

        self.size_summary = {
            "total_bytes_written": self.posix_df['POSIX_BYTES_WRITTEN'].sum(),
            "total_bytes_read": self.posix_df['POSIX_BYTES_READ'].sum(),
            "total_size": self.posix_df['POSIX_BYTES_WRITTEN'].sum() + self.posix_df['POSIX_BYTES_READ'].sum(),     
            "read histogram": read_hist,
            "write histogram": write_hist,
            "top 4 access sizes": top_sizes_dict
        }
        return self.size_summary

    
    def get_request_summary(self):
        total_requests = 0
        total_reads = self.posix_df['POSIX_READS'].sum()
        if total_reads >= 0:
            total_requests += total_reads
        else:
            total_reads = -1
        total_writes = self.posix_df['POSIX_WRITES'].sum()
        if total_writes >= 0:
            total_requests += total_writes
        else:
            total_writes = -1
        total_metadata_operations = 0
        total_mmaps = self.posix_df['POSIX_MMAPS'].sum()
        if total_mmaps >= 0:
            total_metadata_operations += total_mmaps
        else:
            total_mmaps = -1
        total_fsyncs = self.posix_df['POSIX_FSYNCS'].sum()
        if total_fsyncs >= 0:
            total_metadata_operations += total_fsyncs
        else:
            total_fsyncs = -1
        total_fdsyncs = self.posix_df['POSIX_FDSYNCS'].sum()
        if total_fdsyncs >= 0:
            total_metadata_operations += total_fdsyncs
        else:
            total_fdsyncs = -1
        total_opens = self.posix_df['POSIX_OPENS'].sum()
        if total_opens >= 0:
            total_metadata_operations += total_opens
        else:
            total_opens = -1
        total_filenos = self.posix_df['POSIX_FILENOS'].sum()
        if total_filenos >= 0:
            total_metadata_operations += total_filenos
        else:
            total_filenos = -1
        total_dups = self.posix_df['POSIX_DUPS'].sum()
        if total_dups >= 0:
            total_metadata_operations += total_dups
        else:
            total_dups = -1
        total_seeks = self.posix_df['POSIX_SEEKS'].sum()
        if total_seeks >= 0:
            total_metadata_operations += total_seeks
        else:
            total_seeks = -1
        total_stats = self.posix_df['POSIX_STATS'].sum()
        if total_stats >= 0:
            total_metadata_operations += total_stats
        else:
            total_stats = -1
        self.request_summary = {
            "I/O operations":{
                "total": total_requests,
                "reads": total_reads,
                "writes": total_writes,
            },
            "metadata operations":{
                "total": total_metadata_operations,
                "mmaps": total_mmaps,
                "fsyncs": total_fsyncs,
                "fdatasyncs": total_fdsyncs,
                "opens": total_opens,
                "filenos": total_filenos,
                "dups": total_dups,
                "seeks": total_seeks,
                "stats": total_stats
            }
        }
        return self.request_summary

    def get_metadata_summary(self):
        total_metadata_operations = 0
        total_mmap = self.posix_df['POSIX_MMAPS'].sum()
        if total_mmap >= 0:
            total_metadata_operations += total_mmap
        else:
            total_mmap = -1
        total_fsyncs = self.posix_df['POSIX_FSYNCS'].sum()
        if total_fsyncs >= 0:
            total_metadata_operations += total_fsyncs
        else:
            total_fsyncs = -1
        total_fdsyncs = self.posix_df['POSIX_FDSYNCS'].sum()
        if total_fdsyncs >= 0:
            total_metadata_operations += total_fdsyncs
        else:
            total_fdsyncs = -1
        total_opens = self.posix_df['POSIX_OPENS'].sum()
        if total_opens >= 0:
            total_metadata_operations += total_opens
        else:
            total_opens = -1
        total_filenos = self.posix_df['POSIX_FILENOS'].sum()
        if total_filenos >= 0:
            total_metadata_operations += total_filenos
        else:
            total_filenos = -1
        total_dups = self.posix_df['POSIX_DUPS'].sum()
        if total_dups >= 0:
            total_metadata_operations += total_dups
        else:
            total_dups = -1
        total_seeks = self.posix_df['POSIX_SEEKS'].sum()
        if total_seeks >= 0:
            total_metadata_operations += total_seeks
        else:
            total_seeks = -1
        total_stats = self.posix_df['POSIX_STATS'].sum()
        if total_stats >= 0:
            total_metadata_operations += total_stats
        else:
            total_stats = -1

        # calculate the sum over all files, this may exceed total runtime 
        # if there are many files and ranks because they are done in parallel
        total_metadata_time = self.posix_df['POSIX_F_META_TIME'].sum()
        if total_metadata_time >= 0:
            avg_metadata_op_time = total_metadata_time / total_metadata_operations
            avg_metadata_time_per_file = total_metadata_time / len(self.posix_df["record_id"].unique())
            avg_metadata_op_time_per_rank = total_metadata_time / self.posix_df["rank"].nunique()

                
        else:
            avg_metadata_op_time = 0
            avg_metadata_time_per_file = 0
            avg_metadata_op_time_per_rank = 0
        self.metadata_summary = {
            "total metadata time": self.posix_df['POSIX_F_META_TIME'].sum(),
            "average metadata operation time": avg_metadata_op_time,
            "average metadata time per file": avg_metadata_time_per_file,
            "average metadata operation time per rank": avg_metadata_op_time_per_rank,
            "total metadata operations": total_metadata_operations,
            "total mmap": total_mmap,
            "total fsyncs": total_fsyncs,
            "total fdatasyncs": total_fdsyncs,
            "total opens": total_opens,
            "total filenos": total_filenos,
            "total dups": total_dups,
            "total seeks": total_seeks,
            "total stats": total_stats
        }
        return self.metadata_summary
    
    def get_order_summary(self):
        total_reads = self.posix_df['POSIX_READS'].sum()
        total_writes = self.posix_df['POSIX_WRITES'].sum()
        total_consec_reads = self.posix_df['POSIX_CONSEC_READS'].sum()
        total_consec_writes = self.posix_df['POSIX_CONSEC_WRITES'].sum()
        total_seq_reads = self.posix_df['POSIX_SEQ_READS'].sum()
        total_seq_writes = self.posix_df['POSIX_SEQ_WRITES'].sum()
        total_rw_switches = self.posix_df['POSIX_RW_SWITCHES'].sum()
        self.order_summary = {
            "total reads": total_reads,
            "total writes": total_writes,
            "total consecutive reads": total_consec_reads,
            "total consecutive writes": total_consec_writes,
            "total sequential reads": total_seq_reads,
            "total sequential writes": total_seq_writes,
            "total read/write switches": total_rw_switches,
            "top 5 files": {}
        }
        #get the top 4 stride sizes and counts for the top 5 files
        top_files = self.posix_df[["file_name", "POSIX_READS", "POSIX_WRITES"]].groupby("file_name").sum()
        top_files["total_requests"] = top_files[["POSIX_READS", "POSIX_WRITES"]].sum(axis=1)
        top_files = top_files[top_files["total_requests"] > 0].sort_values("total_requests", ascending=False).head(5)
        top_files = self.posix_df.loc[self.posix_df["file_name"].isin(top_files.index)]
        top_sizes_dict = {}
        for i in range(4):
            stride_size_key = f"POSIX_STRIDE{i+1}_STRIDE"
            count_key = f"POSIX_STRIDE{i+1}_COUNT"
            top_sizes_dict[f"stride_{i+1}"] = {"size": dict(zip(top_files["file_name"], top_files[stride_size_key])), "count": dict(zip(top_files["file_name"], top_files[count_key]))}
        self.order_summary["top 4 strides"] = top_sizes_dict
        # only consecutive offsets are guaranteed to not be random access patterns as sequential only means that the offsets are increasing
        order_stats = self.posix_df.groupby("file_name")[["POSIX_READS", "POSIX_WRITES", "POSIX_CONSEC_READS", "POSIX_CONSEC_WRITES", "POSIX_SEQ_READS", "POSIX_SEQ_WRITES", "POSIX_RW_SWITCHES"]].sum()
        # find the top 5 files
        order_stats["total requests"] = order_stats.sum(axis=1)
        top_files = order_stats.sort_values("total requests", ascending=False).head(5).index.to_list()
        order_stats = order_stats.drop(columns=["total requests"])

        for counter, files_dict in order_stats.items():
            for file_name, val in files_dict.items():
                if file_name in top_files:
                    if file_name not in self.order_summary["top 5 files"]:
                        self.order_summary["top 5 files"][file_name] = {}
                    self.order_summary["top 5 files"][file_name][counter] = val
        
        return self.order_summary


    def get_alignment_summary(self):
        total_requests = self.posix_df['POSIX_READS'].sum() + self.posix_df['POSIX_WRITES'].sum()
        self.alignment_summary = {
            "top 5 file alignment sizes": self.posix_df['POSIX_FILE_ALIGNMENT'].value_counts().head(5).to_dict(),
            "file alignment summary stats": {
                "min": self.posix_df['POSIX_FILE_ALIGNMENT'].min(),
                "max": self.posix_df['POSIX_FILE_ALIGNMENT'].max(),
                "mean": self.posix_df['POSIX_FILE_ALIGNMENT'].mean(),
                "std": self.posix_df['POSIX_FILE_ALIGNMENT'].std()
            },
            "top 5 memory alignment sizes": self.posix_df['POSIX_MEM_ALIGNMENT'].value_counts().head(5).to_dict(),
            "memory alignment summary stats": {
                "min": self.posix_df['POSIX_MEM_ALIGNMENT'].min(),
                "max": self.posix_df['POSIX_MEM_ALIGNMENT'].max(),
                "mean": self.posix_df['POSIX_MEM_ALIGNMENT'].mean(),
                "std": self.posix_df['POSIX_MEM_ALIGNMENT'].std()
            }
        }
        if total_requests > 0:
            self.alignment_summary["proportion not aligned"] = self.posix_df.groupby("file_name")['POSIX_FILE_NOT_ALIGNED'].sum()/total_requests
            self.alignment_summary["proportion not aligned"] = self.alignment_summary["proportion not aligned"].sort_values(ascending=False)
            self.alignment_summary["total not aligned"] = self.posix_df.groupby("file_name")['POSIX_FILE_NOT_ALIGNED'].sum()
            self.alignment_summary["total not aligned"] = self.alignment_summary["total not aligned"].sort_values(ascending=False)  
            if len(self.alignment_summary["proportion not aligned"]) > 10:
                self.alignment_summary["proportion not aligned"] = self.alignment_summary["proportion not aligned"].head(10).to_dict()
                self.alignment_summary["total not aligned"] = self.alignment_summary["total not aligned"].head(10).to_dict()
            else:
                self.alignment_summary["proportion not aligned"] = self.alignment_summary["proportion not aligned"].to_dict()
                self.alignment_summary["total not aligned"] = self.alignment_summary["total not aligned"].to_dict()
        else:
            self.alignment_summary["proportion not aligned"] = -1
            self.alignment_summary["total not aligned"] = -1
        return self.alignment_summary

    def get_file_summary(self):
        self.file_summary = {}
        # get the top 10 files by size written
        top_files_write = self.posix_df[["file_name", "POSIX_BYTES_WRITTEN"]].groupby("file_name").sum()
        top_files_write = top_files_write[top_files_write["POSIX_BYTES_WRITTEN"] > 0].sort_values("POSIX_BYTES_WRITTEN", ascending=False).head(10)
        self.file_summary["top files write"] = top_files_write.to_dict()
        # get the top 10 files by size read
        top_files_read = self.posix_df[["file_name", "POSIX_BYTES_READ"]].groupby("file_name").sum()
        top_files_read = top_files_read[top_files_read["POSIX_BYTES_READ"] > 0].sort_values("POSIX_BYTES_READ", ascending=False).head(10)
        self.file_summary["top files read"] = top_files_read.to_dict()
        # get the top 10 files by number of requests
        top_files_requests = self.posix_df[["file_name", "POSIX_READS", "POSIX_WRITES"]].groupby("file_name").sum()
        top_files_requests["total requests"] = top_files_requests["POSIX_READS"] + top_files_requests["POSIX_WRITES"]
        top_files_requests = top_files_requests[top_files_requests["total requests"] > 0].sort_values("total requests", ascending=False).head(10)
        self.file_summary["top files requests"] = top_files_requests.to_dict()
        # get the top 10 files by metadata time
        top_files_metadata = self.posix_df[["file_name", "POSIX_F_META_TIME"]].groupby("file_name").sum()
        top_files_metadata = top_files_metadata[top_files_metadata["POSIX_F_META_TIME"] > 0].sort_values("POSIX_F_META_TIME", ascending=False).head(10)
        self.file_summary["top files metadata"] = top_files_metadata.to_dict()

        self.file_summary["unique files"] = len(self.posix_df["record_id"].unique())
        # UNKNOWN fs means that it is logging to <STDOUT> or <STDERR>
        self.file_summary["unique files by fs"] = self.posix_df.groupby("fs_type")["file_name"].nunique().to_dict()
        files_by_rank = self.posix_df.groupby("rank")["file_name"].nunique()
        self.file_summary["mean unique files accessed by rank"] = files_by_rank.mean()
        self.file_summary["min unique files accessed by rank"] = files_by_rank.min()
        self.file_summary["max unique files accessed by rank"] = files_by_rank.max()
        self.file_summary["std unique files accessed by rank"] = files_by_rank.std()
        self.file_summary["median unique files accessed by rank"] = files_by_rank.median()
        self.file_summary["top 5 ranks by unique files accessed"] = files_by_rank.sort_values(ascending=False).head(5).to_dict()
        self.file_summary["bottom 5 ranks by unique files accessed"] = files_by_rank.sort_values(ascending=True).head(5).to_dict()

        return self.file_summary
    
    def get_rank_summary(self):
        total_ranks = len(self.posix_df["rank"].unique())
        if '-1' in self.posix_df["rank"].unique():
            total_ranks = total_ranks - 1
        # if total_ranks is 0, set it to nprocs because -1 means all ranks
        if total_ranks == 0:
            total_ranks = self.nprocs

        if total_ranks > 10:
            per_rank_write_value = {}
            per_rank_write_key = "average size written per rank"
            per_rank_write_value["average size written per rank"] = self.posix_df.groupby("rank")["POSIX_BYTES_WRITTEN"].sum().mean()
            per_rank_write_value["minimum size written per rank"] = self.posix_df.groupby("rank")["POSIX_BYTES_WRITTEN"].sum().min()
            per_rank_write_value["maximum size written per rank"] = self.posix_df.groupby("rank")["POSIX_BYTES_WRITTEN"].sum().max()
            per_rank_read_value = {}
            per_rank_read_key = "average size read per rank"
            per_rank_read_value["average size read per rank"] = self.posix_df.groupby("rank")["POSIX_BYTES_READ"].sum().mean()
            per_rank_read_value["minimum size read per rank"] = self.posix_df.groupby("rank")["POSIX_BYTES_READ"].sum().min()
            per_rank_read_value["maximum size read per rank"] = self.posix_df.groupby("rank")["POSIX_BYTES_READ"].sum().max()
            per_rank_metadata_value = {}
            per_rank_metadata_key = "average metadata time per rank"
            per_rank_metadata_value["average metadata time per rank"] = self.posix_df.groupby("rank")["POSIX_F_META_TIME"].sum().mean()
            per_rank_metadata_value["minimum metadata time per rank"] = self.posix_df.groupby("rank")["POSIX_F_META_TIME"].sum().min()
            per_rank_metadata_value["maximum metadata time per rank"] = self.posix_df.groupby("rank")["POSIX_F_META_TIME"].sum().max()
        else:
            per_rank_write_key = "size written per rank"
            per_rank_write_value = self.posix_df.groupby("rank")["POSIX_BYTES_WRITTEN"].sum().to_dict()
            per_rank_read_key = "size read per rank"
            per_rank_read_value = self.posix_df.groupby("rank")["POSIX_BYTES_READ"].sum().to_dict()
            per_rank_metadata_key = "metadata time per rank"
            per_rank_metadata_value = self.posix_df.groupby("rank")["POSIX_F_META_TIME"].sum().to_dict()
        # rank ids of -1 represent all ranks
        self.rank_summary = {
            "total ranks": total_ranks,
            per_rank_write_key: per_rank_write_value,
            per_rank_read_key: per_rank_read_value,
            per_rank_metadata_key: per_rank_metadata_value,
        }
        return self.rank_summary
    

    def summarize(self):
        self.get_size_summary()
        self.get_request_summary()
        self.get_metadata_summary()
        self.get_order_summary()
        self.get_alignment_summary()
        self.get_file_summary()
        self.get_rank_summary()
        return self.size_summary, self.request_summary, self.metadata_summary, self.order_summary, self.alignment_summary, self.file_summary, self.rank_summary
    

class MPIIO:

    def __init__(self, mpiio_df, nprocs):
        self.mpiio_df = mpiio_df
        self.darshan_module = "MPIIO"
        self.nprocs = nprocs

    def get_size_summary(self):
        total_reads = self.mpiio_df['MPIIO_INDEP_READS'].sum() + self.mpiio_df['MPIIO_COLL_READS'].sum() + self.mpiio_df['MPIIO_SPLIT_READS'].sum() + self.mpiio_df['MPIIO_NB_READS'].sum()
        total_writes = self.mpiio_df['MPIIO_INDEP_WRITES'].sum() + self.mpiio_df['MPIIO_COLL_WRITES'].sum() + self.mpiio_df['MPIIO_SPLIT_WRITES'].sum() + self.mpiio_df['MPIIO_NB_WRITES'].sum()
        total_requests = total_reads + total_writes
        # get top 4 access sizes and counts for the 5 files with the most requests
        top_files_requests = self.mpiio_df[["file_name", "MPIIO_INDEP_READS", "MPIIO_INDEP_WRITES", "MPIIO_COLL_READS", "MPIIO_COLL_WRITES", "MPIIO_SPLIT_READS", "MPIIO_SPLIT_WRITES", "MPIIO_NB_READS", "MPIIO_NB_WRITES"]].groupby("file_name").sum()
        top_files_requests["total_requests"] = top_files_requests[["MPIIO_INDEP_READS", "MPIIO_INDEP_WRITES", "MPIIO_COLL_READS", "MPIIO_COLL_WRITES", "MPIIO_SPLIT_READS", "MPIIO_SPLIT_WRITES", "MPIIO_NB_READS", "MPIIO_NB_WRITES"]].sum(axis=1)
        top_files_requests = top_files_requests.sort_values("total_requests", ascending=False).head(5)
        top_files = self.mpiio_df.loc[self.mpiio_df["file_name"].isin(top_files_requests.index)]
        top_files_dict = {}
        for i in range(4):
            size_key = f"MPIIO_ACCESS{i+1}_ACCESS"
            count_key = f"MPIIO_ACCESS{i+1}_COUNT"
            top_files_dict[f"size_{i+1}"] = dict(zip(top_files["file_name"], top_files[size_key]))
            if total_requests > 0:
                top_files_dict[f"count_{i+1}"] = dict(zip(top_files["file_name"], top_files[count_key]/total_requests))
            else:
                top_files_dict[f"count_{i+1}"] = dict(zip(top_files["file_name"], top_files[count_key]))

        read_histogram = {}
        write_histogram = {}
        if total_reads > 0:
            read_histogram = {
                "0-100": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_0_100"].sum() / total_writes).astype(float),
                "100-1k": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_100_1K"].sum() / total_writes).astype(float),
                "1k-10k": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_1K_10K"].sum() / total_writes).astype(float),
                "10k-100k": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_10K_100K"].sum() / total_writes).astype(float),
                "100k-1M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_100K_1M"].sum() / total_writes).astype(float),
                "1M-4M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_1M_4M"].sum() / total_writes).astype(float),
                "4M-10M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_4M_10M"].sum() / total_writes).astype(float),
                "10M-100M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_10M_100M"].sum() / total_writes).astype(float),
                "100M-1G": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_100M_1G"].sum() / total_writes).astype(float),
                "1G+": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_1G_PLUS"].sum() / total_writes).astype(float)
            }
        else:
            read_histogram = {
                "0-100": 0,
                "100-1k": 0,
                "1k-10k": 0,
                "10k-100k": 0,
                "100k-1M": 0,
                "1M-4M": 0,
                "4M-10M": 0,
                "10M-100M": 0,
                "100M-1G": 0,
                "1G+": 0
            }
        if total_writes > 0:
            write_histogram = {
                "0-100": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_0_100"].sum() / total_writes).astype(float),
                "100-1k": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_100_1K"].sum() / total_writes).astype(float),
                "1k-10k": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_1K_10K"].sum() / total_writes).astype(float),
                "10k-100k": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_10K_100K"].sum() / total_writes).astype(float),
                "100k-1M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_100K_1M"].sum() / total_writes).astype(float),
                "1M-4M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_1M_4M"].sum() / total_writes).astype(float),
                "4M-10M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_4M_10M"].sum() / total_writes).astype(float),
                "10M-100M": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_10M_100M"].sum() / total_writes).astype(float),
                "100M-1G": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_100M_1G"].sum() / total_writes).astype(float),
                "1G+": (self.mpiio_df["MPIIO_SIZE_WRITE_AGG_1G_PLUS"].sum() / total_writes).astype(float)
            }
        else:
            write_histogram = {
                "0-100": 0,
                "100-1k": 0,
                "1k-10k": 0,
                "10k-100k": 0,
                "100k-1M": 0,
                "1M-4M": 0,
                "4M-10M": 0,
                "10M-100M": 0,
                "100M-1G": 0,
                "1G+": 0
            }
        self.size_summary = {
            "total_bytes_written": self.mpiio_df['MPIIO_BYTES_WRITTEN'].sum(),
            "total_bytes_read": self.mpiio_df['MPIIO_BYTES_READ'].sum(),
            "total_size": self.mpiio_df['MPIIO_BYTES_WRITTEN'].sum() + self.mpiio_df['MPIIO_BYTES_READ'].sum(),
            "read histogram": read_histogram,
            "write histogram": write_histogram,
            "top files by size": top_files_dict
        }
        return self.size_summary
    
    def get_request_summary(self):
        total_requests = 0
        total_indep_reads = self.mpiio_df['MPIIO_INDEP_READS'].sum()
        if total_indep_reads >= 0:
            total_requests += total_indep_reads
        else:
            total_indep_reads = -1
        total_indep_writes = self.mpiio_df['MPIIO_INDEP_WRITES'].sum()
        if total_indep_writes >= 0:
            total_requests += total_indep_writes
        else:
            total_indep_writes = -1
        total_coll_reads = self.mpiio_df['MPIIO_COLL_READS'].sum()
        if total_coll_reads >= 0:
            total_requests += total_coll_reads
        else:
            total_coll_reads = -1
        total_coll_writes = self.mpiio_df['MPIIO_COLL_WRITES'].sum()
        if total_coll_writes >= 0:
            total_requests += total_coll_writes
        else:
            total_coll_writes = -1
        total_split_reads = self.mpiio_df['MPIIO_SPLIT_READS'].sum()
        if total_split_reads >= 0:
            total_requests += total_split_reads
        else:
            total_split_reads = -1
        total_split_writes = self.mpiio_df['MPIIO_SPLIT_WRITES'].sum()
        if total_split_writes >= 0:
            total_requests += total_split_writes
        else:
            total_split_writes = -1
        total_nb_reads = self.mpiio_df['MPIIO_NB_READS'].sum()
        if total_nb_reads >= 0:
            total_requests += total_nb_reads
        else:
            total_nb_reads = -1
        total_nb_writes = self.mpiio_df['MPIIO_NB_WRITES'].sum()
        if total_nb_writes >= 0:
            total_requests += total_nb_writes
        else:
            total_nb_writes = -1
        total_metadata_operations = 0
        total_syncs = self.mpiio_df['MPIIO_SYNCS'].sum()
        if total_syncs >= 0:
            total_metadata_operations += total_syncs
        else:
            total_syncs = -1
        total_views = self.mpiio_df['MPIIO_VIEWS'].sum()
        if total_views >= 0:
            total_metadata_operations += total_views
        else:
            total_views = -1
        total_coll_opens = self.mpiio_df['MPIIO_COLL_OPENS'].sum()
        if total_coll_opens >= 0:
            total_metadata_operations += total_coll_opens
        else:
            total_coll_opens = -1
        
        self.request_summary = {
            "I/O operations": {
                "total": total_requests,
                "independent reads": total_indep_reads,
                "independent writes": total_indep_writes,
                "collective reads": total_coll_reads,
                "collective writes": total_coll_writes,
                "collective opens": total_coll_opens,
                "split reads": total_split_reads,
                "split writes": total_split_writes,
                "non-blocking reads": total_nb_reads,
                "non-blocking writes": total_nb_writes,
            },
            "metadata operations": {
                "total": total_metadata_operations,
                "syncs": total_syncs,
                "views": total_views,
                "collective opens": total_coll_opens
            }
        }
        return self.request_summary
    
    def get_metadata_summary(self):
        total_metadata_requests = 0
        total_syncs = self.mpiio_df['MPIIO_SYNCS'].sum()
        if total_syncs >= 0:
            total_metadata_requests += total_syncs
        else:
            total_syncs = -1
        total_views = self.mpiio_df['MPIIO_VIEWS'].sum()
        if total_views >= 0:
            total_metadata_requests += total_views
        else:
            total_views = -1
        total_coll_opens = self.mpiio_df['MPIIO_COLL_OPENS'].sum()
        if total_coll_opens >= 0:
            total_metadata_requests += total_coll_opens
        else:
            total_coll_opens = -1
        total_metadata_time = self.mpiio_df['MPIIO_F_META_TIME'].sum()
        if total_metadata_time >= 0:
            total_metadata_requests += total_metadata_time
        else:
            total_metadata_time = -1
        # calculate total metadata time per rank
        
        # if the number of ranks is greater than 5, calculate the average, min, max, std, and median metadata time per rank
        total_md_time_rank = {
            "average": self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().mean(),
            "min": self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().min(),
            "max": self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().max(),
            "std": self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().std(),
            "median": self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().median()
        }
        top_5_md_time_ranks = self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().sort_values(ascending=False).head(5)
        bottom_5_md_time_ranks = self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().sort_values(ascending=True).head(5)
 
        self.metadata_summary = {
            "total metadata requests": total_metadata_requests,
            "total syncs": total_syncs,
            "total views": total_views,
            "total collective opens": total_coll_opens,
            "total metadata time": total_metadata_time,
            "metadata time per rank": total_md_time_rank,
            "top 5 ranks by metadata time": top_5_md_time_ranks.to_dict(),
            "bottom 5 ranks by metadata time": bottom_5_md_time_ranks.to_dict()
        }
        return self.metadata_summary
    
    def get_rank_summary(self):
        total_requests = self.mpiio_df['MPIIO_INDEP_READS'].sum() + self.mpiio_df['MPIIO_INDEP_WRITES'].sum() + self.mpiio_df['MPIIO_COLL_READS'].sum() + self.mpiio_df['MPIIO_COLL_WRITES'].sum() + self.mpiio_df['MPIIO_SPLIT_READS'].sum() + self.mpiio_df['MPIIO_SPLIT_WRITES'].sum() + self.mpiio_df['MPIIO_NB_READS'].sum() + self.mpiio_df['MPIIO_NB_WRITES'].sum()
        total_ranks = len(self.mpiio_df["rank"].unique())
        if '-1' in self.mpiio_df["rank"].unique():
            total_ranks = total_ranks - 1
        # if total_ranks is 0, set it to nprocs because -1 means all ranks
        if total_ranks == 0:
            total_ranks = self.nprocs

        per_rank_write_key = "size written per rank"
        per_rank_write_value = {}
        per_rank_write_value["average size written per rank"] = self.mpiio_df.groupby("rank")["MPIIO_BYTES_WRITTEN"].sum().mean()
        per_rank_write_value["minimum size written per rank"] = self.mpiio_df.groupby("rank")["MPIIO_BYTES_WRITTEN"].sum().min()
        per_rank_write_value["maximum size written per rank"] = self.mpiio_df.groupby("rank")["MPIIO_BYTES_WRITTEN"].sum().max()
        per_rank_read_key = "size read per rank"
        per_rank_read_value = {}
        per_rank_read_value["average size read per rank"] = self.mpiio_df.groupby("rank")["MPIIO_BYTES_READ"].sum().mean()
        per_rank_read_value["minimum size read per rank"] = self.mpiio_df.groupby("rank")["MPIIO_BYTES_READ"].sum().min()
        per_rank_read_value["maximum size read per rank"] = self.mpiio_df.groupby("rank")["MPIIO_BYTES_READ"].sum().max()
        per_rank_metadata_key = "metadata time per rank"
        per_rank_metadata_value = {}
        per_rank_metadata_value["average metadata time per rank"] = self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().mean()
        per_rank_metadata_value["minimum metadata time per rank"] = self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().min()
        per_rank_metadata_value["maximum metadata time per rank"] = self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().max()

        top_ranks_write = self.mpiio_df.groupby("rank")["MPIIO_BYTES_WRITTEN"].sum().sort_values(ascending=False).head(5)
        top_ranks_read = self.mpiio_df.groupby("rank")["MPIIO_BYTES_READ"].sum().sort_values(ascending=False).head(5)
        top_ranks_metadata = self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().sort_values(ascending=False).head(5)
        bottom_ranks_write = self.mpiio_df.groupby("rank")["MPIIO_BYTES_WRITTEN"].sum().sort_values(ascending=True).head(5)
        bottom_ranks_read = self.mpiio_df.groupby("rank")["MPIIO_BYTES_READ"].sum().sort_values(ascending=True).head(5)
        bottom_ranks_metadata = self.mpiio_df.groupby("rank")["MPIIO_F_META_TIME"].sum().sort_values(ascending=True).head(5)
        # if -1 is specified anywhere, it means all available ranks are being used
        self.rank_summary = {
            "total ranks": total_ranks,
            per_rank_write_key: per_rank_write_value,
            per_rank_read_key: per_rank_read_value,
            per_rank_metadata_key: per_rank_metadata_value,
            "top 5 ranks by size written": top_ranks_write.to_dict(),
            "top 5 ranks by size read": top_ranks_read.to_dict(),
            "top 5 ranks by metadata time": top_ranks_metadata.to_dict(),
            "bottom 5 ranks by size written": bottom_ranks_write.to_dict(),
            "bottom 5 ranks by size read": bottom_ranks_read.to_dict(),
            "bottom 5 ranks by metadata time": bottom_ranks_metadata.to_dict()
        }

        return self.rank_summary

    def get_file_summary(self):
        self.file_summary = {}
        # summarize the most important files
        # get the top 10 files by size written
        top_files_write = self.mpiio_df[["file_name", "MPIIO_BYTES_WRITTEN"]].groupby("file_name").sum().sort_values("MPIIO_BYTES_WRITTEN", ascending=False).head(10)
        self.file_summary["top_files_write"] = top_files_write.to_dict()
        # get the top 10 files by size read
        top_files_read = self.mpiio_df[["file_name", "MPIIO_BYTES_READ"]].groupby("file_name").sum().sort_values("MPIIO_BYTES_READ", ascending=False).head(10)
        self.file_summary["top_files_read"] = top_files_read.to_dict()
        # get the top 10 files by number of non-metadata requests
        # requests are the sum of all the operation columns that are not metadata
        top_files_requests = self.mpiio_df[["file_name", "MPIIO_INDEP_READS", 
                                                "MPIIO_INDEP_WRITES", "MPIIO_COLL_READS", "MPIIO_COLL_WRITES", 
                                                "MPIIO_SPLIT_READS", "MPIIO_SPLIT_WRITES", "MPIIO_NB_READS", 
                                                "MPIIO_NB_WRITES"]].groupby("file_name").sum()
        # sum all the operation columns
        top_files_requests["total_requests"] = top_files_requests[["MPIIO_INDEP_READS", 
                                                                            "MPIIO_INDEP_WRITES", "MPIIO_COLL_READS", "MPIIO_COLL_WRITES", 
                                                                            "MPIIO_SPLIT_READS", "MPIIO_SPLIT_WRITES", "MPIIO_NB_READS", 
                                                                            "MPIIO_NB_WRITES"]].sum(axis=1)
        top_files_requests = top_files_requests.sort_values("total_requests", ascending=False).head(10)
        self.file_summary["top_files_requests"] = top_files_requests.to_dict()

        # get the top 10 files by number of metadata requests
        top_files_metadata = self.mpiio_df[["file_name", "MPIIO_SYNCS", "MPIIO_VIEWS"]].groupby("file_name").sum()
        top_files_metadata["total_metadata_requests"] = top_files_metadata[["MPIIO_SYNCS", "MPIIO_VIEWS"]].sum(axis=1)
        top_files_metadata = top_files_metadata.sort_values("total_metadata_requests", ascending=False).head(10)
        self.file_summary["top_files_metadata"] = top_files_metadata.to_dict()

        self.file_summary["unique files accessed"] = len(self.mpiio_df["record_id"].unique())
        # UNKNOWN fs means that it is logging to <STDOUT> or <STDERR>
        self.file_summary["files accessed by file system"] = self.mpiio_df["fs_type"].value_counts().to_dict()

        files_by_rank = self.mpiio_df.groupby("rank")["file_name"].nunique()

        self.file_summary["mean unique files accessed by rank"] = files_by_rank.mean()
        self.file_summary["min unique files accessed by rank"] = files_by_rank.min()
        self.file_summary["max unique files accessed by rank"] = files_by_rank.max()
        self.file_summary["std unique files accessed by rank"] = files_by_rank.std()
        self.file_summary["median unique files accessed by rank"] = files_by_rank.median()
        self.file_summary["top 5 ranks by unique files accessed"] = files_by_rank.sort_values(ascending=False).head(5).to_dict()
        self.file_summary["bottom 5 ranks by unique files accessed"] = files_by_rank.sort_values(ascending=True).head(5).to_dict()

        

        return self.file_summary


    def summarize(self):
        self.get_size_summary()
        self.get_request_summary()
        self.get_metadata_summary()
        self.get_rank_summary()
        self.get_file_summary()
        return self.size_summary, self.request_summary, self.metadata_summary, self.rank_summary, self.file_summary



class LUSTRE:
    def __init__(self, lustre_df):
        self.lustre_df = lustre_df.dropna(subset=["LUSTRE_STRIPE_OFFSET", "LUSTRE_STRIPE_SIZE", "LUSTRE_STRIPE_WIDTH"])
        self.darshan_module = "LUSTRE"

    def get_mount_summary(self):
        mount_pts = self.lustre_df["mount_pt"].unique()
        mdts = {}
        for mount_pt in mount_pts:
            mdts[mount_pt] = int(self.lustre_df[self.lustre_df["mount_pt"] == mount_pt]["LUSTRE_MDTS"].iloc[0])
        osts = {}
        for mount_pt in mount_pts:
            osts[mount_pt] = int(self.lustre_df[self.lustre_df["mount_pt"] == mount_pt]["LUSTRE_OSTS"].iloc[0])
        self.lustre_summary = {
            "mdts_per_mount_pt": mdts,
            "osts_per_mount_pt": osts
        }
        return self.lustre_summary

    def get_stripe_summary(self):
        #summarize the distribution of stripe offsets, sizes, and widths
        stripe_offsets = self.lustre_df["LUSTRE_STRIPE_OFFSET"].value_counts()
        # remove the -1 values
        stripe_offsets = stripe_offsets[stripe_offsets > 0]
        if len(stripe_offsets) == 0:
            stripe_offsets = {"-1": 0}
        else:
            stripe_offsets = stripe_offsets.to_dict()

        stripe_sizes = self.lustre_df["LUSTRE_STRIPE_SIZE"].value_counts()
        stripe_sizes = stripe_sizes[stripe_sizes > 0]
        if len(stripe_sizes) == 0:
            stripe_sizes = {"-1": 0}
        else:
            stripe_sizes = stripe_sizes.to_dict()

        
        stripe_widths = self.lustre_df["LUSTRE_STRIPE_WIDTH"].value_counts()
        stripe_widths = stripe_widths[stripe_widths > 0]
        if len(stripe_widths) == 0:
            stripe_widths = {"-1": 0}
        else:
            stripe_widths = stripe_widths.to_dict()

        self.stripe_summary = {
            "stripe_offset": stripe_offsets,
            "stripe_size": stripe_sizes,
            "stripe_width": stripe_widths
        }
        return self.stripe_summary

    def get_ost_usage_summary(self):
        self.ost_usage_summary = {}
        for mount_pt in self.lustre_df["mount_pt"].unique():
            mount_df = self.lustre_df[self.lustre_df["mount_pt"] == mount_pt]
            file_counts = {}
            rank_counts = {}
            for index, row in mount_df.iterrows():
                # find all LUSTRE_OST_ID_X columns
                for column in mount_df.columns:
                    if "LUSTRE_OST_ID_" in column:
                        ost_id = row[column]
                        file_id = row["record_id"]
                        rank = row["rank"]
                        if ost_id not in file_counts:
                            file_counts[ost_id] = []
                        if ost_id not in rank_counts:
                            rank_counts[ost_id] = []
                        if file_id not in file_counts[ost_id]:
                            file_counts[ost_id].append(file_id)
                        if rank not in rank_counts[ost_id]:
                            rank_counts[ost_id].append(rank)
            num_osts = mount_df["LUSTRE_OSTS"].iloc[0]
            file_counts = {f"OST {ost_id}": len(file_counts[ost_id]) for ost_id in file_counts}
            rank_counts = {f"OST {ost_id}": len(rank_counts[ost_id]) for ost_id in rank_counts}

            self.ost_usage_summary[mount_pt] = {
                "file_counts": file_counts,
                "rank_counts": rank_counts,
                "total_osts": int(num_osts)
            }
        return self.ost_usage_summary

    def summarize(self):
        self.get_mount_summary()
        self.get_stripe_summary()
        self.get_ost_usage_summary()
        return self.lustre_summary, self.stripe_summary, self.ost_usage_summary


DarshanModules = {
    "STDIO": STDIO,
    "POSIX": POSIX,
    "MPI-IO": MPIIO,
    "LUSTRE": LUSTRE
}
            
        
