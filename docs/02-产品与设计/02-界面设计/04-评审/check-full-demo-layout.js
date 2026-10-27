async () => {
  const X=window.XJ, issues=[], errors=[];
  const listener=event=>errors.push(event.message);
  window.addEventListener('error',listener);
  let count=0;
  for(const route of X.routes) {
    for(const mode of Object.keys(route.states)) {
      X.S={...X.initial(),auth:true,verified:true};
      X.go(route.id,mode);
      await new Promise(resolve=>requestAnimationFrame(resolve));
      count++;
      const overflow=[...document.querySelectorAll('body *')].filter(element=>{
        const box=element.getBoundingClientRect();
        return box.width&&(box.left < -1 || box.right > innerWidth+1)
          &&getComputedStyle(element).position!=='absolute'&&!element.closest('.table-wrap');
      }).map(element=>element.className||element.tagName);
      if(!document.getElementById('main')||overflow.length||document.documentElement.scrollWidth>innerWidth)
        issues.push({route:route.id,mode,overflow});
    }
  }
  window.removeEventListener('error',listener);
  X.S=X.initial();X.go('store');
  return {width:innerWidth,routes:X.routes.length,count,issues,errors};
}
