import vcf
import math
import os
import numpy
def density(vcf_file,out_file,genome_length=0,step_size=300,window_size=2000,scale=1000):
    print("the vcf file is :",os.path.abspath(vcf_file))
    print("the snp density file is :",os.path.abspath(out_file))
    loc_dic = {}
    vcf_reader=vcf.Reader(filename =vcf_file)
    loc=[]
    for record in vcf_reader:
        loc.append(record.POS)
    loc.sort()
    for i in loc:
        loc_dic[i]=1
    allKys = loc_dic.keys()
    allKys=list(allKys)
    allKys.sort()
    if(genome_length<=allKys[-1]):
        tot_lg = allKys[-1]
    else:
        tot_lg=genome_length
    print("the total genome size is : ",tot_lg)
    stp=step_size
    print("the step size is : ",stp)
    wind =window_size
    print("the window size is : ",wind)
    print("the value for normalization of the SNP density is : " ,scale)
    eff_lg=math.trunc((tot_lg-wind)/stp)*stp
    print("the effective length is %d: " % eff_lg)
    print("the total length is %d: " % tot_lg)
    wind_dic=[]

    for ii in range(0,eff_lg,stp):
        if ii  not in loc_dic:
            loc_dic[ii]=0
        if (ii+wind)  not in loc_dic:
            loc_dic[ii+wind]=0
        wind_dic += [[ii,wind+ii]]

    if eff_lg  not in loc_dic:
        loc_dic[eff_lg]=0

    if (eff_lg+wind) not in loc_dic:
        loc_dic[eff_lg+wind]=0
    wind_dic += [[eff_lg,eff_lg+wind]]

    allKys=loc_dic.keys()
    allKys=list(allKys)
    allKys.sort()

    out_str=''
    for ech in wind_dic:
        left=allKys.index(ech[0])
        right=allKys.index(ech[1])
        rat=0
        for dd in range(left,right):
            rat+=loc_dic[allKys[dd]]
        out_str+='%d\t%d\t%.4f\n' % (ech[1],rat,rat*1.0*scale/wind)
    output_file=open(out_file,'w')
    output_file.write("Win_start\tSNP_num\tDensity\n")
    output_file.write(out_str)
    output_file.close()



    # *****************************************************************************************

def SNP_anno(anno_file,vcf_file):### store the annotations for all SNPs
    anno_file = open(anno_file, 'r')
    anno_dic={}
    big_sz = 150000000
    ### store the annotations for all SNPs
    buff0,buff1,buff='','',''
    tab_annoPos,tab_snpType,tab_geneNam,tab_geneID=0,1,2,3
    anno_file.readline()
    while True:
        buff1=anno_file.read(big_sz).rstrip()
        if buff1=='':
            buff=buff0+'\n'
        else:
            buff=buff0+buff1
        st=0
        while True:
            ed=buff.find('\n',st+1)
            if ed==-1:
                buff0=buff[st:]
                break
            the_buff=buff[st:ed].lstrip().rstrip('\n')
            the_buff_tmp=the_buff.split('\t')
            the_pos=int(the_buff_tmp[tab_annoPos])
            try:
                anno_geneID = the_buff_tmp[tab_geneID]
            except IndexError:
                anno_geneID = '-'
            try:
                anno_snpType = the_buff_tmp[tab_snpType]
            except IndexError:
                raise ValueError("There is no annotation for the snp: %s" % the_pos)
            try:
                anno_geneNam = the_buff_tmp[tab_geneNam]
            except IndexError:
                anno_geneNam = '-'
            the_anno=[anno_snpType,anno_geneNam,anno_geneID]
            if the_pos not in anno_dic:
                anno_dic[the_pos]=the_anno
            elif the_pos in anno_dic:
                print ("the SNP %d has existed, recheck your SNP list" % the_pos)
                raise ValueError('%d' % the_pos)
            st=ed
        if buff1=='':
            break
    anno_file.close()
    targetAnno_dic={}
    targetOperon_dic={}
    tab_annoPos, tab_snpType, tab_geneNam, tab_geneID = 0, 1, 2, 3
    cunt_empty = 0
    tab_pos, tab_assocAllel, tab_freq, tab_ratio, tab_Chi, tab_pVal = 0, 1, 2, 3, 4, 5
    vcf_reader = vcf.Reader(filename=vcf_file)
    for record in vcf_reader:
        loc = int(record.POS)
        if loc in anno_dic:
            this_anno = anno_dic[loc]  # new codes
            targetAnno_dic[loc] = this_anno  # new codes
            if this_anno[tab_geneID - 1] != '-':  # new codes
                targetOperon_dic[loc] = anno_dic[loc][tab_geneID - 1]
            else:
                cunt_empty += 1  # new codes
                targetOperon_dic[loc] = str(cunt_empty)  # new codes, dealing with the SNPs without geneID
        elif loc not in anno_dic:
            print("can't identify the function of the SNP %d, ignored" % loc)
    return targetAnno_dic,targetOperon_dic

def Operon_manage(operon_file,targetOperon_dic,targetAnno_dic):### profile the gene operons
    tab_annoPos, tab_snpType, tab_geneNam, tab_geneID = 0, 1, 2, 3
    geneRange_dic = {}
    geneOperon_dic={}
    geneOperonRev_dic={}
    targetOperonRev_dic={}
    operon_file = open(operon_file, 'r')
    big_sz = 150000000
    ### profile the gene operons
    tab_operonGeneId, tab_geneSt, tab_geneEd, tab_geneOri, tab_operon = 0, 1, 2, 3, 4
    operon_file.readline()
    buff0, buff1, buff = '', '', ''
    while True:
        buff1 = operon_file.read(big_sz).rstrip()
        if buff1 == '':
            buff = buff0 + '\n'
        else:
            buff = buff0 + buff1
        st = 0
        while True:
            ed = buff.find('\n', st + 1)
            if ed == -1:
                buff0 = buff[st:]
                break
            the_buff = buff[st:ed].lstrip().rstrip('\n')
            the_buff_tmp = the_buff.split('\t')
            the_operon = the_buff_tmp[tab_operon]
            the_geneID = the_buff_tmp[tab_operonGeneId]
            if the_operon == '-':  # new codes
                raise ValueError("The operon of the loci %s is invalid" % the_buff_tmp[tab_geneSt])  # new codes
            range1_tmp, range2_tmp = int(the_buff_tmp[tab_geneSt]), int(the_buff_tmp[tab_geneEd])  # new codes
            range1, range2 = min(range1_tmp, range2_tmp), max(range1_tmp, range2_tmp)  # new codes
            the_range = [range1, range2]  # new codes
            if the_geneID not in geneRange_dic:
                geneRange_dic[the_geneID] = [range1, range2, the_operon, the_geneID]
            elif the_geneID in geneRange_dic:
                raise ValueError("The gene %s has existed! Check your gene list." % the_geneID)
            st = ed
        if buff1 == '':
            break
    all_ranges = list(geneRange_dic.values())
    all_ranges.sort()
    rangeNum = len(all_ranges)
    print("The number of total genes before removing nested genes is %d" % rangeNum)
    k_range10, k_range20 = all_ranges[0][0], all_ranges[0][1]
    for kk in range(1, rangeNum):
        range_val = all_ranges[kk]
        k_range1, k_range2 = range_val[0], range_val[1]
        geneID = range_val[3]
        if k_range1 >= k_range10 and k_range2 <= k_range20:
            print("deleted the gene %s" % geneID)
            del geneRange_dic[geneID]
        elif k_range20 >= k_range1 >= k_range10 and k_range2 > k_range20:
            k_range1_new = k_range20 + 1
            geneRange_dic[geneID][0] = k_range1_new
            print("The range of the gene %s is changed to %d and %d" % (geneID, k_range1_new, k_range2))
            k_range10, k_range20 = k_range1_new, k_range2
        else:
            k_range10, k_range20 = k_range1, k_range2
    all_ranges = list(geneRange_dic.values())
    all_ranges.sort()
    rangeNum = len(all_ranges)
    print("The number of total genes after removing nested genes is %d" % rangeNum)
    for kk in range(0, rangeNum):
        range_val = all_ranges[kk]
        k_range1, k_range2 = range_val[0], range_val[1]
        the_operon = range_val[2]
        if the_operon not in geneOperon_dic:
            geneOperon_dic[the_operon] = [[k_range1, k_range2]]
        elif the_operon in geneOperon_dic:
            geneOperon_dic[the_operon] += [[k_range1, k_range2]]
    operon_file.close()

    # *******************************************************************************
    ### define the range of each gene operon
    operon_kys = geneOperon_dic.keys()
    operon_kys = list(operon_kys)
    for ech_key in operon_kys:
        ech_val = geneOperon_dic[ech_key]
        ech_val.sort()
        new_val = (ech_val[0][0], ech_val[-1][-1])
        geneOperonRev_dic[new_val] = ech_key
    ### re-define the gene operons for target SNPs due to the fact that some operons may include several genes
    print("re-define the gene operons for target SNPs")
    operon_AllRange = geneOperonRev_dic.keys()
    snp_AllPos = list(targetOperon_dic.keys())
    snp_AllPos.sort()
    # print snp_AllPos
    for ech_pos in snp_AllPos:
        for ech_range in operon_AllRange:
            if ech_range[0] <= ech_pos <= ech_range[1]:
                operonNm = geneOperonRev_dic[ech_range]
                targetOperon_dic[ech_pos] = operonNm
                break
        else:
            pass
    ### profile the snp list for each operon:
    for ech_pos in snp_AllPos:  ## the SNPs have been in ascending order
        the_operon = targetOperon_dic[ech_pos]
        if the_operon not in targetOperonRev_dic:
            targetOperonRev_dic[the_operon] = [ech_pos]
        elif the_operon in targetOperonRev_dic:
            targetOperonRev_dic[the_operon] += [ech_pos]
    ### initialize the snp clusters if containing non-synonymous snp:
    targetClustRev_dic={}
    snpOperon_lst = targetOperonRev_dic.keys()
    for ech_operon in snpOperon_lst:
        operonSNP_lst = targetOperonRev_dic[ech_operon]
        for ech_snp in operonSNP_lst:
            ech_snp_type = targetAnno_dic[ech_snp][tab_snpType - 1]
            if ech_snp_type == "CDS_nonSynon":
                targetClustRev_dic[ech_operon] = operonSNP_lst
                break
        else:
            pass
    return snp_AllPos, targetClustRev_dic

def clust_initalize(targetClustRev_dic):
    targetClust_dic={}
    Clust0_lst = list(targetClustRev_dic.keys())
    for ech_ky in Clust0_lst:
        snp_in_clust = targetClustRev_dic[ech_ky]
        for ech_snp_in_clust in snp_in_clust:
            targetClust_dic[ech_snp_in_clust] = ech_ky
    return targetClust_dic

def SNP_dist(snp_AllPos):
    dist_dic={}
    distRev_dic={}
    dist_dic[snp_AllPos[0]] = 0  ## the first element in the distance is 0
    snpAllNum = len(snp_AllPos)
    for ii in range(1, snpAllNum):
        dist_dic[snp_AllPos[ii]] = snp_AllPos[ii] - snp_AllPos[ii - 1] + 1
    for jj in range(0, snpAllNum - 1):
        distRev_dic[snp_AllPos[jj]] = dist_dic[snp_AllPos[jj + 1]]
    distRev_dic[snp_AllPos[snpAllNum - 1]] = 0  ## the last element in the distance i
    return dist_dic,distRev_dic

def func_snpDistAry(func_snpLst,direct,sign,dist_dic,distRev_dic):
    import numpy
    func_distLst=[]
    func_snpLst.sort()
    func_snpLstLg = len(func_snpLst)
    #	func_DistAry=numpy.zeros(func_snpLstLg)
    func_distLst = []
    if direct == "R" and sign == 0:
        for i in range(0, func_snpLstLg):
            func_distLst += [dist_dic[func_snpLst[i]]]
    elif direct == "R" and sign == 1:
        func_distLst = [0]
        for i in range(1, func_snpLstLg):
            func_distLst += [dist_dic[func_snpLst[i]]]
    if direct == "L" and sign == 0:
        for i in range(0, func_snpLstLg):
            func_distLst += [distRev_dic[func_snpLst[i]]]
    elif direct == "L" and sign == 1:
        for i in range(0, func_snpLstLg - 1):
            func_distLst += [distRev_dic[func_snpLst[i]]]
        func_distLst += [0]
    return numpy.array(func_distLst)

def cluster_merge(Clust_Length,Clust_list,targetClustRev_dic,dist_dic,distRev_dic,snp_AllPos,targetClust_dic,recomb_lg,scan_loop,targetOperon_dic,max_dist_cluster,min_num_snp,targetAnno_dic):
    tab_annoPos, tab_snpType, tab_geneNam, tab_geneID = 0, 1, 2, 3
    ClustLg=Clust_Length
    Clust_lst=Clust_list
    extremNum = 10000000
    for ech in range(0, ClustLg):
        ech_clust = Clust_lst[ech]
        snp_in_clust = targetClustRev_dic[ech_clust]  ## all SNPs in this cluster
        snp_in_clust.sort()

        snpNumClust = len(snp_in_clust)
        tot_distClust = snp_in_clust[-1] - snp_in_clust[0] + 1
        cent_posClust = (snp_in_clust[-1] + snp_in_clust[0]) / 2.0  # The center position of the SNPs in this cluster
        dist_ary = func_snpDistAry(snp_in_clust, "R", 1, dist_dic,
                                   distRev_dic)  ## equal to func_snpDistAry(tot_distClust,"L",1)
        tot_NRSD = numpy.square(dist_ary).sum()
        if snpNumClust > 1:
            tot_NRMSD = tot_NRSD * 1.0 / (snpNumClust - 1)
        else:
            tot_NRMSD = 0

        last_snp = snp_in_clust[-1]
        first_snp = snp_in_clust[0]
        last_snpIndx = snp_AllPos.index(last_snp)
        first_snpIndx = snp_AllPos.index(first_snp)

        try:  ## locate right snp
            right_snp = snp_AllPos[last_snpIndx + 1]
        except IndexError:
            right_snp = ''

        try:  ## locate left snp
            left_snp = snp_AllPos[first_snpIndx - 1]
        except IndexError:
            left_snp = ''

        if right_snp != '' and right_snp not in targetClust_dic:  ## singlet snp:
            right_snp_dist = dist_dic[right_snp]
        else:
            right_snp_dist = extremNum

        if left_snp != '' and left_snp not in targetClust_dic:  ## singlet snp:
            left_snp_dist = distRev_dic[left_snp]
        else:
            left_snp_dist = extremNum

        ##     define the order of right snp and left snp // and distance
        if left_snp_dist <= right_snp_dist and right_snp_dist + left_snp_dist < extremNum * 2:
            run_order = [left_snp, right_snp]
            dist_order = [left_snp_dist, right_snp_dist]
        elif right_snp_dist < left_snp_dist and right_snp_dist + left_snp_dist < extremNum * 2:
            run_order = [right_snp, left_snp]
            dist_order = [right_snp_dist, left_snp_dist]
        else:  ## the snps on both sides fall into clusters
            run_order = []
            dist_order = []

        if run_order == []:
            continue
        runOrderLg = len(run_order)
        for gg in range(0, runOrderLg):
            side_snp = run_order[gg]
            if side_snp == '' or side_snp in targetClust_dic:
                continue
            # print ("side_snp is: ",side_snp	)
            side_snp_dist = dist_order[gg]
            tot_distClust_tmp = tot_distClust + side_snp_dist
            tot_NRSD_tmp = tot_NRSD + side_snp_dist * side_snp_dist
            tot_NRMSD_tmp = tot_NRSD_tmp * 1.0 / (snpNumClust)

            if snpNumClust == 1 and 0 < tot_distClust_tmp <= recomb_lg:
                targetClust_dic[side_snp] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                targetClustRev_dic[ech_clust] += [side_snp]
                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp

            #			cent_posClust=cent_posClust+right_snp_dist*0.5

            # print ("merged side_snp is: ",side_snp,tot_NRMSD,tot_NRMSD_tmp)
            elif snpNumClust > 1 and 0 < tot_distClust_tmp <= recomb_lg * 2.0 / 3:
                targetClust_dic[side_snp] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                targetClustRev_dic[ech_clust] += [side_snp]
                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp

            #			cent_posClust=cent_posClust+right_snp_dist*0.5
            #			print ("merged side_snp is: ",side_snp,tot_NRMSD,tot_NRMSD_tmp)
            elif snpNumClust > 1 and (
                    recomb_lg * 1.15 > tot_distClust_tmp > recomb_lg * 2.0 / 3 or side_snp_dist < tot_distClust / (
                    snpNumClust - 1)) and tot_NRMSD_tmp <= tot_NRMSD * 1.1:
                targetClust_dic[side_snp] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                targetClustRev_dic[ech_clust] += [side_snp]
                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp

            #			cent_posClust=cent_posClust+right_snp_dist*0.5
            #			print ("merged side_snp is: ",side_snp,tot_NRMSD,tot_NRMSD_tmp)
            else:
                pass

    # ******************************************************************************
    ## begin merging clusters with neighboring clusters,caution: time-consuming
    Clust_lst_single = list(targetClustRev_dic.keys())
    Clust_lst_single.sort()
    Clust_lst = Clust_lst_single * scan_loop
    ClustLg = len(Clust_lst)

    ClustPass = []
    for ech in range(0, ClustLg):
        ech_clust = Clust_lst[ech]
        # print (ech_clust)
        if ech_clust in ClustPass:
            continue
        snp_in_clust = targetClustRev_dic[ech_clust]  ## all SNPs in this cluster
        snp_in_clust.sort()

        snpNumClust = len(snp_in_clust)
        tot_distClust = snp_in_clust[-1] - snp_in_clust[0] + 1
        cent_posClust = (snp_in_clust[-1] + snp_in_clust[0]) / 2.0  # The center position of the SNPs in this cluster
        dist_ary = func_snpDistAry(snp_in_clust, "R", 1, dist_dic,
                                   distRev_dic)  ## equal to func_snpDistAry(tot_distClust,"L",1)
        tot_NRSD = numpy.square(dist_ary).sum()
        if snpNumClust > 1:
            tot_NRMSD = tot_NRSD * 1.0 / (snpNumClust - 1)
        else:
            tot_NRMSD = 0

        last_snp = snp_in_clust[-1]
        first_snp = snp_in_clust[0]
        last_snpIndx = snp_AllPos.index(last_snp)
        first_snpIndx = snp_AllPos.index(first_snp)

        # print (ech_clust,snp_in_clust)
        # print (tot_distClust,cent_posClust)
        # print (dist_ary,tot_NRMSD)

        try:
            right_snp = snp_AllPos[last_snpIndx + 1]
        except IndexError:
            right_snp = ''

        if right_snp != '' and right_snp not in targetClust_dic:  ## if the right-sided snp does not fall into a cluster
            right_snp_dist = dist_dic[right_snp]
            #	tot_distRight=tot_distClust+right_snp_dist
            tot_distClust_tmp = tot_distClust + right_snp_dist
            tot_NRSD_tmp = tot_NRSD + right_snp_dist * right_snp_dist
            tot_NRMSD_tmp = tot_NRSD_tmp * 1.0 / (snpNumClust)
            if snpNumClust == 1 and 0 < tot_distClust_tmp <= recomb_lg:
                # print ("the single-snp cluster is: ",right_snp,tot_distClust_tmp)
                # print ("merged snp is: ",right_snp,tot_NRMSD,tot_NRMSD_tmp)

                targetClust_dic[right_snp] = ech_clust
                targetClustRev_dic[ech_clust] += [right_snp]

                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust + right_snp_dist * 0.5

            elif snpNumClust > 1 and 0 < tot_distClust_tmp <= recomb_lg * 2.0 / 3:
                # print ("merged snp is: ",right_snp,tot_NRMSD,tot_NRMSD_tmp)

                targetClust_dic[right_snp] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                targetClustRev_dic[ech_clust] += [right_snp]

                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust + right_snp_dist * 0.5
            #		elif snpNumClust > 1 and (recomb_lg * 1.15 > tot_distClust_tmp > recomb_lg * 2.0/3 or right_snp_dist < recomb_lg * 0.25) and tot_NRMSD_tmp <= tot_NRMSD*1.1:
            elif snpNumClust > 1 and (
                    recomb_lg * 1.15 > tot_distClust_tmp > recomb_lg * 2.0 / 3 or right_snp_dist < tot_distClust / (
                    snpNumClust - 1)) and tot_NRMSD_tmp <= tot_NRMSD * 1.1:
                # print ("merged snp is: ",right_snp,tot_NRMSD,tot_NRMSD_tmp)

                targetClust_dic[right_snp] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                targetClustRev_dic[ech_clust] += [right_snp]
                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust + right_snp_dist * 0.5
            else:
                #			ClustPass+=[ech_clust]
                pass

        elif right_snp != '' and right_snp in targetClust_dic:  ## if the right-sided snp falls into a cluster
            right_clust = targetClust_dic[right_snp]
            right_clustSNP = targetClustRev_dic[right_clust]
            snpNumRight = len(right_clustSNP)
            cent_posRight = (right_clustSNP[-1] + right_clustSNP[0]) * 0.5
            dist_AryRight = func_snpDistAry(right_clustSNP, "R", 0, dist_dic, distRev_dic)
            tot_NRSD_tmp = tot_NRSD + numpy.square(dist_AryRight).sum()
            tot_NRMSD_tmp = tot_NRSD_tmp * 1.0 / (snpNumClust - 1 + snpNumRight)
            #		print cent_posRight,cent_posClust,tot_NRMSD_tmp,tot_NRMSD
            #		print (right_snp,right_clust)

            if snpNumClust == 1 and 0 < cent_posRight - cent_posClust <= recomb_lg * 2.0 / 3:
                for ech_rightSNP in right_clustSNP:
                    targetClust_dic[ech_rightSNP] = ech_clust
                targetClustRev_dic[ech_clust] += right_clustSNP
                del targetClustRev_dic[right_clust]
                #			print ("type 1: the original cluster was merged into new cluster ", right_clust,ech_clust)
                tot_distClust = tot_distClust + dist_AryRight.sum()
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust + dist_AryRight.sum() * 0.5

                ClustPass += [right_clust]
            elif snpNumClust > 1 and 0 < cent_posRight - cent_posClust <= recomb_lg * 2.0 / 3:
                for ech_rightSNP in right_clustSNP:  ## update the targetClust_dic and targetClustRev_dic
                    targetClust_dic[ech_rightSNP] = ech_clust
                targetClustRev_dic[ech_clust] += right_clustSNP
                del targetClustRev_dic[right_clust]
                #			print ("type 2: the original cluster was merged into new cluster", right_clust,ech_clust)
                tot_distClust = tot_distClust + dist_AryRight.sum()
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust + dist_AryRight.sum() * 0.5

                ClustPass += [right_clust]

            elif snpNumClust > 1 and recomb_lg * 1.1 > cent_posRight - cent_posClust > recomb_lg * 2.0 / 3 and tot_NRMSD_tmp <= tot_NRMSD * 1.1:
                for ech_rightSNP in right_clustSNP:
                    targetClust_dic[ech_rightSNP] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                targetClustRev_dic[ech_clust] += right_clustSNP
                del targetClustRev_dic[right_clust]
                #			print ("type 3: the original cluster was merged", right_clust)
                tot_distClust = tot_distClust + dist_AryRight.sum()
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust + dist_AryRight.sum() * 0.5

                ClustPass += [right_clust]
            else:
                #			ClustPass+=[ech_clust]
                pass

        try:
            left_snp = snp_AllPos[first_snpIndx - 1]
        except IndexError:
            left_snp = ''
        if left_snp != '' and left_snp not in targetClust_dic:  ## if the left-sided snp does not fall into a cluster
            left_snp_dist = distRev_dic[left_snp]
            #	tot_distRight=tot_distClust+right_snp_dist
            tot_distClust_tmp = tot_distClust + left_snp_dist
            tot_NRSD_tmp = tot_NRSD + left_snp_dist * left_snp_dist
            tot_NRMSD_tmp = tot_NRSD_tmp * 1.0 / (snpNumClust)
            if snpNumClust == 1 and 0 < tot_distClust_tmp <= recomb_lg:
                targetClust_dic[left_snp] = ech_clust
                #			targetClustRev_dic[ech_clust]+=[left_snp]
                targetClustRev_dic[ech_clust].insert(0, left_snp)
                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust - left_snp_dist * 0.5

            #			print ("the single-snp cluster is: ",left_snp,tot_distClust_tmp)
            #			print ("merged snp is: ",left_snp,tot_NRMSD,tot_NRMSD_tmp)
            elif snpNumClust > 1 and 0 < tot_distClust_tmp <= recomb_lg * 2.0 / 3:
                targetClust_dic[left_snp] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                #			targetClustRev_dic[ech_clust]+=[left_snp]
                targetClustRev_dic[ech_clust].insert(0, left_snp)
                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust - left_snp_dist * 0.5

            #			print ("merged snp is: ",left_snp,tot_NRMSD,tot_NRMSD_tmp)
            elif snpNumClust > 1 and (
                    recomb_lg * 1.15 > tot_distClust_tmp > recomb_lg * 2.0 / 3 or left_snp_dist < tot_distClust / (
                    snpNumClust - 1)) and tot_NRMSD_tmp <= tot_NRMSD * 1.1:
                targetClust_dic[left_snp] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                #			targetClustRev_dic[ech_clust]+=[left_snp]
                targetClustRev_dic[ech_clust].insert(0, left_snp)
                tot_distClust = tot_distClust_tmp
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust - left_snp_dist * 0.5

            #			print ("merged snp is: ",left_snp,tot_NRMSD,tot_NRMSD_tmp)
            else:
                #			ClustPass+=[ech_clust]
                pass



        elif left_snp != '' and left_snp in targetClust_dic:  ## if the left-sided snp falls into a cluster
            left_clust = targetClust_dic[left_snp]
            left_clustSNP = targetClustRev_dic[left_clust]
            #		print left_clustSNP
            snpNumLeft = len(left_clustSNP)  ## this parameter only for "left"
            cent_posLeft = (left_clustSNP[-1] + left_clustSNP[0]) * 0.5  ## this parameter only for "left"
            dist_AryLeft = func_snpDistAry(left_clustSNP, "L", 0, dist_dic,
                                           distRev_dic)  ## this parameter only for "left"
            tot_NRSD_tmp = tot_NRSD + numpy.square(dist_AryLeft).sum()
            tot_NRMSD_tmp = tot_NRSD_tmp * 1.0 / (snpNumClust - 1 + snpNumLeft)
            #		print (left_snp,left_clust)
            if snpNumClust == 1 and 0 < cent_posClust - cent_posLeft <= recomb_lg * 2.0 / 3:
                for ech_leftSNP in left_clustSNP:
                    targetClust_dic[ech_leftSNP] = ech_clust
                #			targetClustRev_dic[ech_clust]+=left_clustSNP
                targetClustRev_dic[ech_clust] = left_clustSNP + targetClustRev_dic[ech_clust]
                del targetClustRev_dic[left_clust]
                #			print ("type 1: the original cluster %s was merged into new cluster %s", left_clust,ech_clust)
                tot_distClust = tot_distClust + dist_AryLeft.sum()
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust - dist_AryLeft.sum() * 0.5

                ClustPass += [left_clust]
            elif snpNumClust > 1 and 0 < cent_posClust - cent_posLeft <= recomb_lg * 2.0 / 3:
                for ech_leftSNP in left_clustSNP:  ## update the targetClust_dic and targetClustRev_dic
                    targetClust_dic[ech_leftSNP] = ech_clust
                #			targetClustRev_dic[ech_clust]+=left_clustSNP
                targetClustRev_dic[ech_clust] = left_clustSNP + targetClustRev_dic[ech_clust]
                del targetClustRev_dic[left_clust]
                #			print ("type 2: the original cluster %s was merged into new cluster %s", left_clust,ech_clust)
                tot_distClust = tot_distClust + dist_AryLeft.sum()
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust - dist_AryLeft.sum() * 0.5

                ClustPass += [left_clust]
            elif snpNumClust > 1 and recomb_lg * 1.1 > cent_posClust - cent_posLeft > recomb_lg * 2.0 / 3 and tot_NRMSD_tmp <= tot_NRMSD * 1.1:
                for ech_leftSNP in left_clustSNP:
                    targetClust_dic[ech_leftSNP] = ech_clust  ## update targetClust_dic and targetClustRev_dic
                #			targetClustRev_dic[ech_clust]+=left_clustSNP
                targetClustRev_dic[ech_clust] = left_clustSNP + targetClustRev_dic[ech_clust]
                del targetClustRev_dic[left_clust]
                #			print ("type 3: the original cluster %s was merged into new cluster %s", left_clust,ech_clust)
                tot_distClust = tot_distClust + dist_AryLeft.sum()
                tot_NRSD = tot_NRSD_tmp
                tot_NRMSD = tot_NRMSD_tmp
                cent_posClust = cent_posClust - dist_AryLeft.sum() * 0.5

                ClustPass += [left_clust]
            else:
                #			ClustPass+=[ech_clust]
                pass

    NewClust1_lst = list(targetClustRev_dic.keys())
    NewClust1_lst.sort()
    NewClust1Lg = len(NewClust1_lst)

    # ****************************************************************************************
    ### :
    max_dist_snp = recomb_lg * 2.0 / 3
    # print (NewClust1_lst)
    for ech in range(0, NewClust1Lg):
        ech_NewClust1 = NewClust1_lst[ech]
        snp_in_NewClust1 = targetClustRev_dic[ech_NewClust1]
        snp_in_NewClust1.sort()

        #	print ("order: ", ech_NewClust1)
        snpNumNewClust1 = len(snp_in_NewClust1)
        snpNumNewClust1_tmp = snpNumNewClust1
        totDistNewClust1_tmp = snp_in_NewClust1[-1] - snp_in_NewClust1[0] + 1
        cunt = 0
        mm = 0
        for qq in range(1, snpNumNewClust1):
            #		print (qq,snp_in_NewClust1)
            split_snp = snp_in_NewClust1[qq]
            split_dist = dist_dic[split_snp]
            split_operon = targetOperon_dic[split_snp]
            forw_snp = snp_in_NewClust1[qq - 1]
            forw_operon = targetOperon_dic[forw_snp]

            if split_operon == forw_operon and split_dist > max_dist_cluster:
                cunt += 1
                split_NewClust = ech_NewClust1 + '-' + str(cunt)
                print("the split cluster within the same operon is: ", cunt, split_NewClust)
                for pp in range(mm, qq):
                    targetClust_dic[snp_in_NewClust1[pp]] = split_NewClust  ## split targetClust_dic
                targetClustRev_dic[split_NewClust] = snp_in_NewClust1[mm:qq]
                #	del targetClustRev_dic[ech_NewClust1][mm:qq] ## delete the elements designated to new clusters
                targetClustRev_dic[ech_NewClust1] = snp_in_NewClust1[qq:]
                mm = qq
                snpNumNewClust1_tmp = snpNumNewClust1 - qq
                totDistNewClust1_tmp = snp_in_NewClust1[-1] - snp_in_NewClust1[qq] + 1
            elif snpNumNewClust1_tmp >= 3 and split_operon != forw_operon and totDistNewClust1_tmp >= recomb_lg * 1.1 and split_dist > max_dist_snp:
                cunt += 1
                split_NewClust = ech_NewClust1 + '-' + str(cunt)
                print("the split cluster in different operon is: ", cunt, split_NewClust)
                for pp in range(mm, qq):
                    targetClust_dic[snp_in_NewClust1[pp]] = split_NewClust
                targetClustRev_dic[split_NewClust] = snp_in_NewClust1[mm:qq]
                #	del targetClustRev_dic[ech_NewClust1][mm:qq]
                targetClustRev_dic[ech_NewClust1] = snp_in_NewClust1[qq:]
                mm = qq
                snpNumNewClust1_tmp = snpNumNewClust1 - qq
                totDistNewClust1_tmp = snp_in_NewClust1[-1] - snp_in_NewClust1[qq] + 1

    NewClust2_lst = list(targetClustRev_dic.keys())
    NewClust2_lst.sort()
    NewClust2Lg = len(NewClust2_lst)
    ### sorting the clusters:
    FirstSnp_lst = []
    FirstSnp_dic, clust_order = {}, {}
    for ech in range(0, NewClust2Lg):
        ech_NewClust2 = NewClust2_lst[ech]
        snp_in_NewClust2 = targetClustRev_dic[ech_NewClust2]
        snp_in_NewClust2.sort()
        #	print (ech_NewClust2,snp_in_NewClust2)

        if len(snp_in_NewClust2) < min_num_snp:  ## only keep the clusters with SNPs >= min_mum_snp
            del targetClustRev_dic[ech_NewClust2]
            map(targetClust_dic.__delitem__, filter(targetClust_dic.__contains__, snp_in_NewClust2))
            continue

        snp_NewClust2_type = []
        for ech_snp_NewClust2 in snp_in_NewClust2:  ## only keep the clusters containing non-synonymous SNPs
            ech_snp_NewClust2_type = targetAnno_dic[ech_snp_NewClust2][tab_snpType - 1]
            snp_NewClust2_type += [ech_snp_NewClust2_type]

        if "CDS_nonSynon" not in snp_NewClust2_type:
            del targetClustRev_dic[ech_NewClust2]
            map(targetClust_dic.__delitem__, filter(targetClust_dic.__contains__, snp_in_NewClust2))
            continue

        FirstSnp = snp_in_NewClust2[0]
        if ech_NewClust2 not in FirstSnp_dic:
            FirstSnp_dic[ech_NewClust2] = FirstSnp
            FirstSnp_lst += [FirstSnp]
        elif ech_NewClust2 in FirstSnp_dic:
            print("the cluster %s has existed!" % ech_NewClust2)
    FirstSnp_lst.sort()

    NewClust3_lst = list(targetClustRev_dic.keys())
    NewClust3_lst.sort()
    NewClust3Lg = len(NewClust3_lst)

    for ech in range(0, NewClust3Lg):
        ech_NewClust3 = NewClust3_lst[ech]
        FirstSnp = FirstSnp_dic[ech_NewClust3]

        if ech_NewClust3 not in clust_order:
            clust_order[ech_NewClust3] = FirstSnp_lst.index(FirstSnp) + 1
        elif ech_NewClust3 in clust_order:
            print("the cluster %s has existed!" % ech_NewClust3)
    return clust_order,NewClust3Lg,targetClustRev_dic,NewClust2Lg
def cluster_out(clust_order,NewClust3Lg,targetClustRev_dic,NewClust2Lg,recomb_lg,clust_out):
    clustStr = ''
    NewClust3_lst_sort = sorted(clust_order, key=clust_order.__getitem__)
    cluster_size = []
    for ss in range(NewClust3Lg):
        the_clust = NewClust3_lst_sort[ss]
        the_ClustOrder = clust_order[the_clust]
        the_snp_clust = targetClustRev_dic[the_clust]
        clust_size = len(the_snp_clust)
        cluster_size.append(int(clust_size))
        clust_lg = the_snp_clust[-1] - the_snp_clust[0] + 1
        clustStr += '%d\t%d\t%d\t%d\t%d\n' % (the_ClustOrder, the_snp_clust[0], the_snp_clust[-1], clust_size, clust_lg)
    print("recomb_lg=%d=%d=%d=%d=%.2f" % (recomb_lg, NewClust2Lg, max(cluster_size), min(cluster_size), sum(cluster_size) / len(cluster_size)))
    output_clust = open(clust_out, 'w')
    output_clust.write("ClusterID\tFirstSNP\tLastSNP\tClusterSize\tClusterLength\n")
    output_clust.write(clustStr)
    output_clust.close()

def cluster_Pval(cluster_file,out_file,rate):
    import os
    from scipy import stats
    print("The snp cluster file is:",os.path.abspath(cluster_file))
    print("The output file providing the p-value of clustering for each SNP cluster is :",os.path.abspath(out_file))
    print("the pre-estimated average mutation rate is :",rate)
    mutRate = float(rate)
    clust_file=open(cluster_file,'r')
    next(clust_file)
    #mutRate=0.0001
    big_sz=100000000
    buff0,buff1,buff='','',''
    clustID_tab,clustSiz_tab,clustLg_tab=0,3,4
    outStr=''
    while True:
        buff1=clust_file.read(big_sz).rstrip()
        if buff1 == '':
            buff=buff0+'\n'
        else:
            buff=buff0+buff1

        st=0
        while True:
            ed=buff.find('\n',st+1)
            if ed==-1:
                buff0=buff[st:]
                break
            the_buff=buff[st:ed].lstrip().rstrip('\n')
            the_buff_tmp=the_buff.split('\t')
            clust_size=int(the_buff_tmp[clustSiz_tab])
            clust_lg=int(the_buff_tmp[clustLg_tab])
            clust_ID=the_buff_tmp[clustID_tab]

            pVal=stats.gamma.cdf(clust_lg,clust_size,loc=0,scale=1.0/mutRate)
            outStr+='%s\t%d\t%d\t%.4f\n' % (clust_ID,clust_size,clust_lg,pVal)
            st=ed
        if buff1=='':
            break

    clust_file.close()
    output_file=open(out_file,'w')
    output_file.write("ID\tSNP_num\tlength\tp-value\n")
    output_file.write(outStr)
    output_file.close()