(this.webpackJsonpinterface=this.webpackJsonpinterface||[]).push([[0],{44:function(e,t,n){},46:function(e,t){},73:function(e,t,n){},74:function(e,t,n){"use strict";n.r(t);var r=n(7),c=n.n(r),a=n(31),o=n.n(a),i=(n(44),n(23)),s=n.n(i),u=n(32),l=n(14),d=n(15),p=n(18),j=n(17),v=n(39),f=(n(71),n(6)),h=function(e){Object(p.a)(n,e);var t=Object(j.a)(n);function n(){var e;Object(l.a)(this,n);for(var r=arguments.length,c=new Array(r),a=0;a<r;a++)c[a]=arguments[a];return(e=t.call.apply(t,[this].concat(c))).player=void 0,e.videoNode=void 0,e}return Object(d.a)(n,[{key:"componentDidMount",value:function(){this.player=Object(v.a)(this.videoNode,this.props).ready((function(){}))}},{key:"componentWillUnmount",value:function(){var e;null===(e=this.player)||void 0===e||e.dispose()}},{key:"render",value:function(){var e=this;return console.log("render"),Object(f.jsxs)("div",{className:"c-player",children:[Object(f.jsx)("div",{className:"c-player__screen","data-vjs-player":"true",children:Object(f.jsx)("video",{ref:function(t){return e.videoNode=t},className:"video-js"})}),"                "]})}}]),n}(r.Component),O=(n(73),function(e){Object(p.a)(n,e);var t=Object(j.a)(n);function n(e){var r;return Object(l.a)(this,n),(r=t.call(this,e)).state={streams:[]},r}return Object(d.a)(n,[{key:"componentDidMount",value:function(){var e=Object(u.a)(s.a.mark((function e(){var t;return s.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,fetch("/config.json");case 2:return e.next=4,e.sent.json();case 4:t=e.sent,this.setState({streams:t.map((function(e){return{name:e.Name,url:e.Forwarder}}))});case 6:case"end":return e.stop()}}),e,this)})));return function(){return e.apply(this,arguments)}}()},{key:"render",value:function(){var e=this.state.streams.map((function(e){return{name:e.name,srcObject:{src:e.url,type:"application/x-mpegURL"}}}));return Object(f.jsx)("div",{className:"App",children:Object(f.jsx)("header",{className:"App-header",children:e&&e.map((function(e){return Object(f.jsxs)("div",{children:[Object(f.jsx)("h1",{children:e.name}),Object(f.jsx)(h,{autoplay:!0,controls:!0,sources:[e.srcObject]},e.name)]})}))})})}}]),n}(c.a.Component));console.log("test: production"),console.log("Environment variable: "+Object({NODE_ENV:"production",PUBLIC_URL:"",WDS_SOCKET_HOST:void 0,WDS_SOCKET_PATH:void 0,WDS_SOCKET_PORT:void 0,FAST_REFRESH:!0}).REACT_APP_URL);var m=O,b=function(e){e&&e instanceof Function&&n.e(3).then(n.bind(null,75)).then((function(t){var n=t.getCLS,r=t.getFID,c=t.getFCP,a=t.getLCP,o=t.getTTFB;n(e),r(e),c(e),a(e),o(e)}))};o.a.render(Object(f.jsx)(c.a.StrictMode,{children:Object(f.jsx)(m,{})}),document.getElementById("root")),b()}},[[74,1,2]]]);
//# sourceMappingURL=main.f999950d.chunk.js.map