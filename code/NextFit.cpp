#include <algorithm>
#include <iostream>
#include <fstream>
#include<ctime>
#include <chrono>
using namespace std;

#define NoLimit 100000//����һ��ʼ�Ļ��ܵ�����Ϊ����

struct Bin{//�������ӵĽṹ
    double x;//���ӷ��õ�x����
    double y;//���ӷ��õ�y����
    double height;//���ӵĸ߶�
    double width;//���ӵĿ��
    
    friend bool operator < (const Bin& i1, const Bin& i2){
        return i1.height>i2.height;
    }
};

int main(){
    //���ļ�
    ifstream file;
    file.open("test.txt", ios::in);
    if(file.is_open()) cout << "�ļ��򿪳ɹ�" << endl;
    else cout << "�ļ���ʧ��" << endl;
    
    //���ļ��е����ݶ�ȡ����
    int i,n; file>>n;//��ȡ��������
    double optH;
    struct Bin bin[n];
    for(i=0;i<n;i++){//��ȡÿ�����ӵĿ�Ⱥ͸߶�
        file>>bin[i].height>>bin[i].width;
    }
    file>>optH;
    file.close();//�ر��ļ�
    
    clock_t startTime,endTime;
    startTime = clock();//��ʱ��ʼ
    
    sort(bin,bin+n);//���ߣ������е����ӵĸ߶Ȱ��մӸߵ�������
    
    double this_width,this_height;//��ǰ�����������ӵĸ߶ȺͿ��
    double allWidth = 1;//��ǰ���ܵĿ�ȣ���Ϊ1
    double allHeight = 0;//���ܵ��ܸ߶ȣ���ʼ��Ϊ0
    double currentX = 0,currentY = 0;;//��ǰ��һ������Ҳ�����ʣ�ռ�����½����꣬��ʼΪ��0��0��
    double currentShelfHeight=NoLimit;//��ǰ���ܵ��޸ߣ������ǰ������û�����ӣ���ô�޸�ΪNoLimit
                                      //��������ӣ���ô�޸�Ϊ��һ������Ҳ������ߵ����ӵĸ߶�
    
    for(i=0;i<n;i++){
        this_width=bin[i].width;//��ֵ
        this_height=bin[i].height;//��ֵ
        if(this_width>allWidth-currentX||this_height>currentShelfHeight){
            //����һ�л��ܵ�ʣ����С�ڲ������ӵĿ�� ���� ��һ�л��ܵ�ʣ��߶�С�ڲ������ӵĸ߶� ��ʱ��
            //�ͽ��²�������ӷ�����һ��
            bin[i].x=0;bin[i].y=currentShelfHeight;//�����������ӵ����½�����
            currentY+=currentShelfHeight;//����
            currentX=this_width;//����
            currentShelfHeight=this_height;//����
        }else{
            //���Է�����һ�����
            bin[i].x=currentX;bin[i].y=currentY;//�����������ӵ����½�����
            currentX=currentX+this_width;//����
            //����һ�����û����Ʒ��ʱ�򣬽���һ����ܵ��޸�����Ϊ�Լ��ĸ߶�
            if(currentShelfHeight==NoLimit)currentShelfHeight=this_height;
        }
    }
    
    endTime = clock();
    
    //cout << "The run time is: " <<(double)(endTime - startTime)  << "ms" << endl;
    
    allHeight=currentY+currentShelfHeight;//���»����ܸ߶�
    cout<<"���Ÿ߶�:"<<optH<<endl;
    cout<<"�ܹ��߶�:"<<allHeight<<endl;
    cout<<"ApRatio"<<allHeight/optH<<endl;
    //���ÿ�����ӵģ�x���꣬y���꣩�����ӿ�� ���Ӹ߶�
    /*for(i=0;i<n;i++){
        cout<<i+1<<":("<<bin[i].x<<","<<bin[i].y<<"):"<<bin[i].width<<" "<<bin[i].height<<endl;
    }*/
    
    return 0;
}
