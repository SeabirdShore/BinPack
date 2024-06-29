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
    double allHeight=0;//����������ܸ߶�
    cout<<"����n����Ϊ"<<cuts+1<<"�ı���:";
    cin>>n;
    
    struct Node bin[n];
    
    srand((unsigned)time(NULL));
    double last_width=1;//ά��һ����Ҫ�и�ľ��Σ���ʼ���Ϊ1
    double last_height=0;//ά��һ����Ҫ�и�ľ��Σ��߶���Ҫ�������
    
    double h;
    
    i=0;
    int times=cuts;//��ʼ��timesΪcuts��ʹ��һ��ʼ����Ҫ��������һ���������
    while(i<n){
        if(times==cuts){//���и���κ���Ҫ�������ɾ���
            if(i!=0){//���˵�һ�Σ����������Ҫ���и��ʣ��ľ���Ҳ����
                bin[i].height=last_height;
                bin[i].width=last_width;
                i++;
                if(i==n)break;
            }
            
            times=0;//��Ϊ0
            last_height=(double)rand()/RAND_MAX;//������ɸ߶�
            while(last_height<0.5)last_height=(double)rand()/RAND_MAX;//ʹ�ø߶ȱ���>0.5
            last_width=1;
            allHeight+=last_height;//���¸߶�
        }
        
        h=(double)rand()/RAND_MAX;//�������һ���и�ı���
        //cout<<times<<":h="<<h<<endl;
        
        if(times%2==0){//��һ�����У������������ν���
            if((double)rand()/RAND_MAX>0.5){//���ѡ�����Ĳ���
                //д���������
                bin[i].height=last_height;
                bin[i].width=last_width*(1-h);
                //��ά��ʣ��ĸ߶ȺͿ��
                last_width=last_width*h;
            }else{
                //д���������
                bin[i].height=last_height;
                bin[i].width=last_width*h;
                //��ά��ʣ��ĸ߶ȺͿ��
                last_width=last_width*(1-h);
            }
        }else{
            if((double)rand()/RAND_MAX>0.5){//���ѡ�����Ĳ���
                //д���������
                bin[i].width=last_width;
                bin[i].height=last_height*(1-h);
                //��ά��ʣ��ĸ߶ȺͿ��
                last_height=last_height*h;
            }else{
                //д���������
                bin[i].width=last_width;
                bin[i].height=last_height*h;
                //��ά��ʣ��ĸ߶ȺͿ��
                last_height=last_height*(1-h);
            }
        }
        
        
        //�����Ҫÿ������width<height
//        for(int j=i;j<i+12;j++){
//            if(bin[j].width>bin[j].height)swap(bin[j].width,bin[j].height);
//        }
        //�����תÿ������
        if((double)rand()/RAND_MAX>0.5)swap(bin[i].width,bin[i].height);
        
        i++;
        times++;
    }
    //д���ļ�
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
