#include <algorithm>
#include <iostream>
#include <fstream>
#include <time.h>
#define cuts 8
using namespace std;

struct Node{
    double height;
    double width;
};

int main(){
    int i,n;
    double allHeight=0;//最终输出的总高度
    cout<<"输入n必须为"<<cuts+1<<"的倍数:";
    cin>>n;
    
    struct Node bin[n];
    
    srand((unsigned)time(NULL));
    double last_width=1;//维护一个需要切割的矩形，初始宽度为1
    double last_height=0;//维护一个需要切割的矩形，高度需要随机生成
    
    double h;
    
    i=0;
    int times=cuts;//初始化times为cuts，使得一开始就需要重新生成一个随机矩形
    while(i<n){
        if(times==cuts){//当切割五次后需要重新生成矩形
            if(i!=0){//除了第一次，其他情况需要将切割后剩余的矩形也保存
                bin[i].height=last_height;
                bin[i].width=last_width;
                i++;
                if(i==n)break;
            }
            
            times=0;//置为0
            last_height=(double)rand()/RAND_MAX;//随机生成高度
            while(last_height<0.5)last_height=(double)rand()/RAND_MAX;//使得高度必须>0.5
            last_width=1;
            allHeight+=last_height;//更新高度
        }
        
        h=(double)rand()/RAND_MAX;//随机生成一个切割的比例
        //cout<<times<<":h="<<h<<endl;
        
        if(times%2==0){//第一次竖切，横切竖切依次进行
            if((double)rand()/RAND_MAX>0.5){//随机选择保留的部分
                //写入矩形数组
                bin[i].height=last_height;
                bin[i].width=last_width*(1-h);
                //再维护剩余的高度和宽度
                last_width=last_width*h;
            }else{
                //写入矩形数组
                bin[i].height=last_height;
                bin[i].width=last_width*h;
                //再维护剩余的高度和宽度
                last_width=last_width*(1-h);
            }
        }else{
            if((double)rand()/RAND_MAX>0.5){//随机选择保留的部分
                //写入矩形数组
                bin[i].width=last_width;
                bin[i].height=last_height*(1-h);
                //再维护剩余的高度和宽度
                last_height=last_height*h;
            }else{
                //写入矩形数组
                bin[i].width=last_width;
                bin[i].height=last_height*h;
                //再维护剩余的高度和宽度
                last_height=last_height*(1-h);
            }
        }
        
        
        //如果需要每个箱子width<height
//        for(int j=i;j<i+12;j++){
//            if(bin[j].width>bin[j].height)swap(bin[j].width,bin[j].height);
//        }
        //随机翻转每个箱子
        if((double)rand()/RAND_MAX>0.5)swap(bin[i].width,bin[i].height);
        
        i++;
        times++;
    }
    //写入文件
    ofstream ofs;
    ofs.open("test.txt", ios::out);
    ofs<<n<<endl;
    
    for(i=0;i<n;i++){
        ofs<<bin[i].height<<" "<<bin[i].width<<endl;
        //cout<<bin[i].height<<" "<<bin[i].width<<endl;
    }
    ofs<<allHeight<<endl;
    return 0;
}
