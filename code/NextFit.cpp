#include <algorithm>
#include <iostream>
#include <fstream>
#include<ctime>
#include <chrono>
using namespace std;

#define NoLimit 100000//定义一开始的货架的上限为无穷

struct Bin{//定义箱子的结构
    double x;//箱子放置的x坐标
    double y;//箱子放置的y坐标
    double height;//箱子的高度
    double width;//箱子的宽度
    
    friend bool operator < (const Bin& i1, const Bin& i2){
        return i1.height>i2.height;
    }
};

int main(){
    //打开文件
    ifstream file;
    file.open("test.txt", ios::in);
    if(file.is_open()) cout << "文件打开成功" << endl;
    else cout << "文件打开失败" << endl;
    
    //将文件中的内容读取进来
    int i,n; file>>n;//读取箱子总数
    double optH;
    struct Bin bin[n];
    for(i=0;i<n;i++){//读取每个箱子的宽度和高度
        file>>bin[i].height>>bin[i].width;
    }
    file>>optH;
    file.close();//关闭文件
    
    clock_t startTime,endTime;
    startTime = clock();//计时开始
    
    sort(bin,bin+n);//离线，将所有的箱子的高度按照从高到低排列
    
    double this_width,this_height;//当前插入的这个箱子的高度和宽度
    double allWidth = 1;//当前货架的宽度，定为1
    double allHeight = 0;//货架的总高度，初始化为0
    double currentX = 0,currentY = 0;;//当前这一层货架右部分所剩空间的左下角坐标，初始为（0，0）
    double currentShelfHeight=NoLimit;//当前货架的限高：如果当前货架上没有箱子，那么限高为NoLimit
                                      //如果有箱子，那么限高为第一个箱子也就是最高的箱子的高度
    
    for(i=0;i<n;i++){
        this_width=bin[i].width;//赋值
        this_height=bin[i].height;//赋值
        if(this_width>allWidth-currentX||this_height>currentShelfHeight){
            //当这一行货架的剩余宽度小于插入箱子的宽度 或者 这一行货架的剩余高度小于插入箱子的高度 的时候
            //就将新插入的箱子放在下一层
            bin[i].x=0;bin[i].y=currentShelfHeight;//保存插入的箱子的左下角坐标
            currentY+=currentShelfHeight;//更新
            currentX=this_width;//更新
            currentShelfHeight=this_height;//更新
        }else{
            //可以放在这一层货架
            bin[i].x=currentX;bin[i].y=currentY;//保存插入的箱子的左下角坐标
            currentX=currentX+this_width;//更新
            //当这一层货架没有物品的时候，将这一层货架的限高设置为自己的高度
            if(currentShelfHeight==NoLimit)currentShelfHeight=this_height;
        }
    }
    
    endTime = clock();
    
    //cout << "The run time is: " <<(double)(endTime - startTime)  << "ms" << endl;
    
    allHeight=currentY+currentShelfHeight;//更新货架总高度
    cout<<"最优高度:"<<optH<<endl;
    cout<<"总共高度:"<<allHeight<<endl;
    cout<<"ApRatio"<<allHeight/optH<<endl;
    //输出每个箱子的（x坐标，y坐标）：箱子宽度 箱子高度
    /*for(i=0;i<n;i++){
        cout<<i+1<<":("<<bin[i].x<<","<<bin[i].y<<"):"<<bin[i].width<<" "<<bin[i].height<<endl;
    }*/
    
    return 0;
}
