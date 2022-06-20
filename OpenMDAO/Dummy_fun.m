function fitness = Dummy_fun(x)

xorg = x;
%cost of pumping gw per actor
gw_cost = [0.1,0.2,0.12,1.2,1];
%cost of pumping sw per actor
sw_cost = [1,.5,.2,0.1,0.05];

%%
%Parameters of fertilized application functions per crop
p_crops_a = [-.3,-.1,-.05];
p_crops_b = [4000,5000,3000];
f_cost = [500,400,200];

% Sale price per unit of yield for different crops
crops_price = [200,500,100];

%Cost of fertilizer as a function of total irrigation amount
 cost = [];
for i = 1:3
    for ii = 0:100
       if round((1 + (0.8*-exp(p_crops_a(i)*ii)))) ~= 1 
          cost(ii+1,i) = ii*f_cost(i);
       else
          cost(ii+1,i) = cost((ii+1)-1,i);
       end
    end
end

% Max. Yield of crops based on irrigation amount (Water consumption per crop)
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

%x = reshape(x,5,4)';
x = reshape(x,1,4)';

for i = 1:length(x(1,:))
%     if x(1,i)+ x(2,i) <= 100
        WR = (x(1,i)+ x(2,i));
        cost_f = interp1([0:100],cost(:,x(4,i)),WR); % cost of fertilizer
        yield = interp1(w_crops(:,1),w_crops(:,x(3,i)),WR); % Max. Yield of crop
        if yield == 0
            cost_f = 0;
        end
        per_yield = 1 + (0.8*-exp(p_crops_a(x(3,i))*WR)); % Perc. of Max yield
        profit(i,1) = yield*per_yield*crops_price(x(3,i)) - (x(1,i)*gw_cost(i) + x(2,i)*sw_cost(i)) - cost_f; % profit function
        envir(i,1) = (1 + (0.8*-exp(p_crops_a(x(4,i))*WR))).*p_crops_b(x(4,i)); % enviromental cost function
%     else
%         % Penalty multipliers if violation of constraints
%         profit(i,1) = -1000000000;
%         envir(i,1) =   1000000000;
%     end
end

total_val = sum(profit) + sum(envir);
rj = 0.5;
fitness = rj*(sum(profit)/total_val)*-1 +  (sum(envir)/total_val)*(1-rj);

%fitness(1,1) = (sum(profit)/total_val)*-1;  
%fitness(1,2) = (sum(envir)/total_val);

end