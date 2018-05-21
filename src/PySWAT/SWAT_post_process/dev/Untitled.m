a = 1.0;
b = 5.1/(4.0*pi()^2);
c = 5.0/pi();
d = 6.0;
e = 10.0;
f = 1.0/(8.0*pi());

cj = 1;
%for x0 = [-1000:10:1000]
for x0 = [-5:1:10]
    ci = 1;
    for x1 = [0:0.001:15]
        fitness(ci,cj) = a*(x1 - b*x0^2 + c*x0 - d)^2 + e*(1-f)*cos(x0) + e;
        fitness2(ci,cj) = x0^2 + c*x0*x1;
        ci = ci + 1;
    end
    cj = cj + 1;
end
[x,y] = meshgrid([-5:1:10],[0:0.001:15]);

%%
%subplot(1,2,1);surf(x,y,fitness);shading flat;
surf(x,y,fitness);shading flat;
xlabel('x0')
ylabel('x1')
hold on
%subplot(1,2,2);surf(x,y,fitness2);shading flat
maxval = max(fitness(:)/range(fitness(:))+fitness2(:)/range(fitness2(:)));
[row,cols] = find(fitness/range(fitness(:))+fitness2/range(fitness2(:)) == maxval);

[x(row,cols),y(row,cols)];


minval = min(fitness(:));
[row,cols] = find(fitness == minval);
[x(row,cols),y(row,cols)]

minval2 = min(fitness2(:));
[row2,cols2] = find(fitness2 == minval2);
[x(row2,cols2),y(row2,cols2)]

surf(x,y,fitness2);shading flat
xlabel('x0')
ylabel('x1')

%%
% subplot(1,2,1)
% imagesc([-5:1:10],[0:0.001:15],fitness)
% xlabel('x0')
% ylabel('x1')
% 
% subplot(1,2,2)
% imagesc([-5:1:10],[0:0.001:15],fitness2)
% xlabel('x0')
% ylabel('x1')

%%
figure(3)
subplot(1,2,1);
surf(x,y,fitness);shading flat;
xlabel('x0')
ylabel('x1')
hold on
subplot(1,2,2);
surf(x,y,fitness2);shading flat
xlabel('x0')
ylabel('x1')
