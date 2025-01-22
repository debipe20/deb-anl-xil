%01/17/2018: added 1-1 line
%01/18/2018: removed 1-1 line
%09/01/2019: Return handle
function [a,f,gof,h]=plot_lin_fit(x,y)

    x=reshape(x,[],1);
    y=reshape(y,[],1);
    x(isnan(y+x))=nan;
    y(isnan(x+y))=nan;
    M=max([x;y;1]);
    m=min([x;y;0]);
    
    [f,gof]=fit(x,y,'poly1','Exclude',isnan(x+y));
    
    x_sorted=sort(x);
    h(1)=scatter(x,y,20,'MarkerFaceColor','k','MarkerFaceAlpha',min(1,1/length(x)^0.3*2),'MarkerEdgeColor','none');
    hold on;
    h(2) = plot(x_sorted,f(x_sorted),'-r','Linewidth',2);
    grid on;
    
    ax=gca;ax.Units='normalized';
    str={['Slope = ',num2str(round(f.p1,5))],['Intercept = ',num2str(round(f.p2,2))],['R^2 = ',num2str(round(gof.rsquare,2))],['\rho = ',num2str(round(nancorr(x,y),2))]};
%     axis equal;axis([m M m M]) 
    plotboxpos = [0.1471    0.7629    0.2175    0.1438];
    a=annotation('textbox',plotboxpos,'String',str,'FitBoxToText','on','FontSize',10,'Color','k','Linestyle','none');box on;   
%     h(3) = plot([m M],[m M],'--b','Linewidth',2);
    
end