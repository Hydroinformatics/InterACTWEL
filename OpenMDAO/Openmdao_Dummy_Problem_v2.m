clear all
%cost of pumping gw per actor
gw_cost = [0.1,0.2,0.12,1.2,1];
%cost of pumping sw per actor
sw_cost = [1,.5,.2,0.1,0.05];

%%
% Sale price per unit of yield for different crops
crops_price = [200,500,100];

%Parameters of fertilized application functions per crop
p_crops_a = [-.3,-.1,-.05]; 
p_crops_b = [4000,5000,3000];
f_cost = [500,400,200]; %

% Per of Max. yield given a fertilizer choice (assumed to be similar
% regardless of the crop choice -> Not true)

% subplot(1,3,1)
% for i = 1:3
%     hold on;
%     plot([0:100],1 + (0.8*-exp(p_crops_a(i).*[0:100])))
% end
% xlabel('Irrigation amount (water units)');
% ylabel('Perc. of Max. Yield');
% legend('F-1','F-2','F-3');
% grid on;

%Environmental degradation/cost
% subplot(1,3,2)
% for i = 1:3
%     hold on;
%     plot([0:100],(1 + (0.8*-exp(p_crops_a(i).*[0:100]))).*p_crops_b(i));
% end
% xlabel('Irrigation amount (water units)');
% ylabel('Environmental Cost');
% legend('F-1','F-2','F-3');
% grid on;

%Cost of fertilizer as a function of total irrigation amount
% subplot(1,3,3)
% cost = [];
for i = 1:3
    %hold on;
    
    for ii = 0:100
       if round((1 + (0.8*-exp(p_crops_a(i)*ii)))) ~= 1 
          cost(ii+1,i) = ii*f_cost(i);
       else
          cost(ii+1,i) = cost((ii+1)-1,i);
       end
    end
    %plot([0:100],cost(:,i));
end
% xlabel('Irrigation amount (water units)');
% ylabel('Fertilizer Cost');
% legend('F-1','F-2','F-3');
% grid on;

%% Max. Yield of crops based on irrigation amount (Water consumption per crop)
w_crops = [0	0	0	0;
           10	0	0	0;
           20	60	0	200;
           30	180	80	300;
           40	250	150	310;
           50	280	300	320;
           60	400	450	330;
           70	420	500	340;
           80	460	550	350;
           100	500	600	360];

% figure;
% for i = 1:3
%     hold on;
%     plot(w_crops(:,1),w_crops(:,i+1))
% end
% grid on;
% set(gca,'xlim',[0 100]);
% legend('C-1','C-2','C-3');
% xlabel('Irrigation amount (water units)');
% ylabel('Max. Yield');

%% Optimize allocation of water - Genetic Algorithm
% Total available resources
SW = 100;
GW = 100;

% Upper and lower boundaries for decision variables
% 1-5 = GW amount , 6-10 = SW amount, 11-15 = Crop choice, 16-20 = Fertilizer choice
%lb = [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1];
%ub = [100,100,100,100,100,100,100,100,100,100,3,3,3,3,3,3,3,3,3,3];

lb = [0,0,1,1];
ub = [100,100,3,3];

% Constraints the individual sum <= Total resources
% A(1,:) = [ones(1,5),zeros(1,5),zeros(1,5),zeros(1,5)];
% b(1) = 100;
% A(2,:) = [zeros(1,5),ones(1,5),zeros(1,5),zeros(1,5)];
% b(2) = 100;

A(1,:) = [1,1,0,0];
b(1) = 100;
%A(2,:) = [0,1,0,0];
%b(2) = 100;

% Used to speed up the convergance 
% Constraints the individual sum >= Total resources*90%
% A(3,:) = [-1*ones(1,5),zeros(1,5),zeros(1,5),zeros(1,5)];
% b(3) = -90;
% A(4,:) = [zeros(1,5),-1*ones(1,5),zeros(1,5),zeros(1,5)];
% b(4) = -90;

% A(3,:) = [-1*ones(1,1),zeros(1,1),zeros(1,1),zeros(1,1)];
% b(3) = -90;
% A(4,:) = [zeros(1,1),-1*ones(1,1),zeros(1,1),zeros(1,1)];
% b(4) = -90;

% Results = [];
% save Results Results

% Run GA (parameters were selected to speed-up covergance -> Not optimal)
fun = @Dummy_fun;
options = optimoptions('ga','PlotFcn',@Dummy_fun,'MaxGenerations',200,'PopulationSize',100,'PlotFcn',{@gaplotbestf,@gaplotstopping});
[x, fval] = ga(fun,4,A,b,[],[],lb,ub,[],[3:4],options);

%options = optimoptions('gamultiobj','OutputFcn',@Dummy_fun);
%[x, fval] = gamultiobj(@Dummy_fun,4,A,b,[],[],lb,ub,[],[3:4],options);

x
fval

% %% Load action plans (list of all individual chromosomes evaluated)
% load Results
% 
% % Eliminate results that violate constraints
% temp_wr = find(sum(Results(:,[1:5]),2) <= 100 & sum(Results(:,[6:10]),2) <= 100);
% Results = Results(temp_wr,:);
% temp_wr = find(sum(double(Results <= -1000000000 | Results >= 1000000000),2) == 0);
% Results = Results(temp_wr,:);
% 
% % Cluster results to find some of the most distinct solutions
% Z = linkage(Results,'ward');
% c = cluster(Z,'Maxclust',500);
% 
% k=[];
% for i = 1:length(unique(c))
%     k(i,1) = find(c==i,1);
% end
% 
% arjan_data = Results(k,:);
% 
% %% Sort results to apply ranking (Per farmer philosophy)
% [~,ind1]=sort(arjan_data(:,21),'descend');
% [~,ind1] = sort(ind1,'ascend');
% 
% [~,ind2]=sortrows(arjan_data(:,[22,27]),[-1,2]); 
% [~,ind2] = sort(ind2,'ascend');
% 
% [~,ind3]=sortrows([sum(arjan_data(:,[26:30]),2),arjan_data(:,23)],[1,-2]);
% [~,ind3] = sort(ind3,'ascend');
% 
% [~,ind4]=sortrows([sum(arjan_data(:,[21:25]),2),arjan_data(:,24)],[-1,-2]);
% [~,ind4] = sort(ind4,'ascend');
% 
% [~,ind5]=sortrows([sum(arjan_data(:,[26:30]),2),arjan_data(:,25),sum(arjan_data(:,[21:25]),2)],[2,-1,-3]);
% [~,ind5] = sort(ind5,'ascend');
% 
% Rankings = [arjan_data,[ind1,ind2,ind3,ind4,ind5]];
% 
% %% From sorting to Ranking (5-star ranking)
% IND = [ind1,ind2,ind3,ind4,ind5];
% temp_ind(IND<=10) = 1;
% temp_ind(IND>10 & IND<=20) = 2;
% temp_ind(IND>20 & IND<=30) = 3;
% temp_ind(IND>30 & IND<=40) = 4;
% temp_ind(IND>40 & IND<=50) = 5;
% 
