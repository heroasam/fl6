function a0_0x3307(_0x37fff9,_0x263cf3){const _0x36a04f=a0_0x36a0();return a0_0x3307=function(_0x330787,_0x171778){_0x330787=_0x330787-0x94;let _0x3d6488=_0x36a04f[_0x330787];return _0x3d6488;},a0_0x3307(_0x37fff9,_0x263cf3);}(function(_0x2e148a,_0x3eb7ea){const _0x207ebd=a0_0x3307,_0x54bc8c=_0x2e148a();while(!![]){try{const _0x5ee5d3=-parseInt(_0x207ebd(0x120))/0x1*(parseInt(_0x207ebd(0x136))/0x2)+-parseInt(_0x207ebd(0xde))/0x3+-parseInt(_0x207ebd(0xea))/0x4+-parseInt(_0x207ebd(0x108))/0x5+-parseInt(_0x207ebd(0xa2))/0x6+parseInt(_0x207ebd(0x134))/0x7*(parseInt(_0x207ebd(0xb9))/0x8)+parseInt(_0x207ebd(0x12e))/0x9*(parseInt(_0x207ebd(0x12a))/0xa);if(_0x5ee5d3===_0x3eb7ea)break;else _0x54bc8c['push'](_0x54bc8c['shift']());}catch(_0x39a644){_0x54bc8c['push'](_0x54bc8c['shift']());}}}(a0_0x36a0,0x4d0eb));function FfAJZZH0ytHuiD0aIFCFlNpfO(){return{'cliente':{'dni':'','nombre':'','calle':'','num':'','acla':'','barrio':'','tel':'','wapp':'','dnigarante':'','cuota_requerida':'','arts':''},'calles':[],'barrios':[],'articulos':[],'nombregarante':'','direcciongarante':'','obtenerCalles'(){const _0x27d522=a0_0x3307;axios['get'](_0x27d522(0x9d))['then'](_0x22350f=>{const _0x2bd691=_0x27d522;this[_0x2bd691(0xa3)]=_0x22350f[_0x2bd691(0xed)][_0x2bd691(0xd2)];});},'obtenerBarrios'(){const _0xb0fe8=a0_0x3307;axios[_0xb0fe8(0xbe)](_0xb0fe8(0x11f))[_0xb0fe8(0x130)](_0x5e7753=>{const _0x1dae58=_0xb0fe8;this[_0x1dae58(0x139)]=_0x5e7753[_0x1dae58(0xed)][_0x1dae58(0xd2)];});},'buscarDni'(_0x19ac7d){const _0x567b10=a0_0x3307;axios['get'](_0x567b10(0x13f)+_0x19ac7d)[_0x567b10(0x130)](_0x2f9842=>{const _0x293267=_0x567b10;this['cliente']=_0x2f9842['data']['cliente'],msgSuccess(_0x293267(0x124));});},'buscaGarante'(_0x528527){const _0x1d7dc6=a0_0x3307;this[_0x1d7dc6(0x160)][_0x1d7dc6(0x10e)]!=''&&axios['get'](_0x1d7dc6(0xd8)+this[_0x1d7dc6(0x160)][_0x1d7dc6(0x10e)])[_0x1d7dc6(0x130)](_0x2835a5=>{const _0x14ecfb=_0x1d7dc6;this[_0x14ecfb(0xcb)]=_0x2835a5['data'][_0x14ecfb(0xc6)][0x0][_0x14ecfb(0x98)],this[_0x14ecfb(0xcd)]=_0x2835a5[_0x14ecfb(0xed)][_0x14ecfb(0xc6)][0x0][_0x14ecfb(0x10d)];})[_0x1d7dc6(0x101)](_0x55af5d=>msgError(_0x1d7dc6(0x102)));},'validarClienteNuevo'(){const _0x3ce9e2=a0_0x3307;if(this[_0x3ce9e2(0x160)][_0x3ce9e2(0xa5)]==''){msgError(_0x3ce9e2(0x12b));return;}if(this[_0x3ce9e2(0x160)][_0x3ce9e2(0x98)]==''){msgError('Debe\x20ingresar\x20el\x20Nombre');return;}if(this[_0x3ce9e2(0x160)]['calle']==''||!this[_0x3ce9e2(0xa3)][_0x3ce9e2(0xd0)](this[_0x3ce9e2(0x160)][_0x3ce9e2(0x104)])){msgError(_0x3ce9e2(0x112));return;}if(this[_0x3ce9e2(0x160)]['num']==''){msgError(_0x3ce9e2(0x14f));return;}if(this[_0x3ce9e2(0x160)]['barrio']==''||!this[_0x3ce9e2(0x139)]['includes'](this[_0x3ce9e2(0x160)]['barrio'])){msgError(_0x3ce9e2(0x11a));return;}if(this[_0x3ce9e2(0x160)]['cuota_requerida']==''){msgError(_0x3ce9e2(0x121));return;}if(this['cliente'][_0x3ce9e2(0x14e)]==''){msgError(_0x3ce9e2(0xf6));return;}this[_0x3ce9e2(0x141)]();},'pedirAutorizacion'(){const _0x3138b8=a0_0x3307;idButton=document['getElementById']('buttonPedirAutorizacion'),idButton[_0x3138b8(0xba)]=!![],axios[_0x3138b8(0xee)][_0x3138b8(0x152)][_0x3138b8(0x151)][_0x3138b8(0xfe)]=this['$refs']['token'][_0x3138b8(0xa4)],axios[_0x3138b8(0x14d)](_0x3138b8(0x99),this[_0x3138b8(0x160)])[_0x3138b8(0x130)](_0x21b2a2=>{const _0x37bcbe=_0x3138b8;if(_0x21b2a2[_0x37bcbe(0xed)][_0x37bcbe(0x115)]==0x1){msgError('Error',_0x37bcbe(0x15b),0x2710);return;}this[_0x37bcbe(0x160)][_0x37bcbe(0xc0)]=_0x21b2a2[_0x37bcbe(0xed)]['idautorizacion'],msgSuccess('autorizacion\x20enviada.\x20Espere\x20la\x20repuesta.');let _0x3906e0=_0x37bcbe(0x135)+this[_0x37bcbe(0x160)]['nombre']+'\x0acomo\x20CLIENTE\x20NUEVO.\x0aQuedo\x20a\x20la\x20espera.\x20Gracias.',_0x347ae9=_0x37bcbe(0xe5),_0x1f7e6a={'msg':_0x3906e0,'tipo':_0x347ae9};axios[_0x37bcbe(0xee)]['headers'][_0x37bcbe(0x151)]['X-CSRF-TOKEN']=this[_0x37bcbe(0xec)][_0x37bcbe(0xaa)][_0x37bcbe(0xa4)],axios[_0x37bcbe(0x14d)](_0x37bcbe(0x96),_0x1f7e6a)[_0x37bcbe(0x130)](_0xea608f=>{let _0x285c6e=0x0,_0x4c04bf=setInterval(()=>{const _0xb67c2c=a0_0x3307;axios[_0xb67c2c(0xbe)](_0xb67c2c(0xc8)+this[_0xb67c2c(0x160)]['idautorizacion'])[_0xb67c2c(0x130)](_0x3b0b76=>{const _0x3da10b=_0xb67c2c;_0x285c6e=_0x3b0b76[_0x3da10b(0xed)][_0x3da10b(0xa6)];if(_0x285c6e==0x1){msgDelay(_0x3da10b(0x11b),0x493e0),clearTimeout(_0x4c04bf);let _0x4847e7=setInterval(()=>{const _0x2b3ec6=_0x3da10b;axios[_0x2b3ec6(0xbe)]('/ymIVWKdjgnCeJvo2zcodwRTQM/'+this[_0x2b3ec6(0x160)][_0x2b3ec6(0xc0)])[_0x2b3ec6(0x130)](_0x29c27b=>{const _0x38ca94=_0x2b3ec6;switch(_0x29c27b[_0x38ca94(0xed)][_0x38ca94(0x9a)]){case _0x38ca94(0x107):msgSuccess(_0x38ca94(0x15e),_0x38ca94(0x155),0x2710),clearTimeout(_0x4847e7),setTimeout(()=>{const _0x3406c9=_0x38ca94;window[_0x3406c9(0xb0)]=_0x3406c9(0x12c);},0x2774);break;case'sigueigual':msgWarning(_0x38ca94(0x15f),'La\x20cuota\x20no\x20fue\x20autorizada.\x20Se\x20puede\x20vender\x20hasta\x20la\x20cuota\x20basica.',0x2710),clearTimeout(_0x4847e7),setTimeout(()=>{const _0x514d30=_0x38ca94;window[_0x514d30(0xb0)]=_0x514d30(0x12c);},0x2774);break;case'rechazado':msgError(_0x38ca94(0xd9),'El\x20dato\x20ha\x20sido\x20rechazado.\x20No\x20se\x20le\x20puede\x20vender',0x2710),clearTimeout(_0x4847e7),setTimeout(()=>{const _0x41d202=_0x38ca94;window[_0x41d202(0xb0)]='/2xxXix5cnz7IKcYegqs6qf0R6';},0x2774);break;}});},0x2710);}});},0x2710);});});}};}function DRpCmN0kdtSCE2mWXi5CiVycj(){return{'listaVisitasVendedor':[],'listaVisitasVendedor_':[],'listaFechas':[],'listaFechas_':[],'fecha':'','vdor':'','listaVendedores':[],'getVisitasVendedor'(){const _0x3b5fbe=a0_0x3307;axios[_0x3b5fbe(0xbe)](_0x3b5fbe(0x11e))[_0x3b5fbe(0x130)](_0x50a50c=>{const _0x131aa8=_0x3b5fbe;this[_0x131aa8(0x12d)]=_0x50a50c[_0x131aa8(0xed)][_0x131aa8(0xe4)],this[_0x131aa8(0x12d)][_0x131aa8(0xdc)](_0x23d4c2=>_0x23d4c2['fecha']=dayjs['utc'](_0x23d4c2['fecha'])['format']('YYYY-MM-DD')),this[_0x131aa8(0x140)]=_0x50a50c[_0x131aa8(0xed)][_0x131aa8(0xb7)],this['listaFechas'][_0x131aa8(0xdc)](_0x2f1121=>_0x2f1121[_0x131aa8(0xcf)]=dayjs['utc'](_0x2f1121[_0x131aa8(0xcf)])[_0x131aa8(0xc7)](_0x131aa8(0x150))),this[_0x131aa8(0xd5)]=this[_0x131aa8(0x140)],this[_0x131aa8(0xd5)][_0x131aa8(0xd4)]();});},'expandChildren'(_0x1ebab2){const _0x29d939=a0_0x3307;if(this['fecha']==_0x1ebab2&&this[_0x29d939(0x149)][_0x29d939(0x9b)]>0x0){this[_0x29d939(0x149)]=[];return;}this[_0x29d939(0x149)]=this[_0x29d939(0x12d)][_0x29d939(0x128)](_0x5f3f8c=>_0x5f3f8c[_0x29d939(0xfd)]==this['vdor']),this[_0x29d939(0x149)]=this['listaVisitasVendedor'][_0x29d939(0x128)](_0x344fe2=>_0x344fe2['fecha']==_0x1ebab2),this['fecha']=_0x1ebab2,setTimeout(()=>{const _0x20eb9f=_0x29d939;$tbody=document[_0x20eb9f(0xe9)](_0x20eb9f(0xda)),$trfecha=document[_0x20eb9f(0xc4)](_0x1ebab2);let _0x43ca93=Array[_0x20eb9f(0x109)]($tbody[_0x20eb9f(0xad)]),_0x4c6a97=_0x43ca93['filter'](_0x1ac152=>_0x1ac152[_0x20eb9f(0xaf)][_0x20eb9f(0x10a)](_0x20eb9f(0xad)));_0x4c6a97=_0x4c6a97['reverse']();for(el of _0x4c6a97){$tbody[_0x20eb9f(0x9f)](el,$trfecha[_0x20eb9f(0xbb)]);}},0xa);},'filtrarVdor'(_0x487154){const _0x55671e=a0_0x3307;this[_0x55671e(0xfd)]=_0x487154,this[_0x55671e(0xd5)]=this[_0x55671e(0x140)][_0x55671e(0x128)](_0x331cfd=>_0x331cfd['vdor']==_0x487154);}};}function BuuZZCDVMyzK4I1OcGEvNeeob(){return{'listadoDatos':[],'listadoDatos_':[],'listaItemsDatos':[],'agrupar':'','listaArticulos':[],'listaArtComprados':[],'Articulos':[],'Dato':{},'Datos':{},'cuota_basica':'','verCard':![],'Venta':{'cnt':'','art':''},'dnivalidado':![],'dnigarantevalidado':![],'sumaCuota':'','verNotificacionAutorizacion':![],'nombregarante':'','direcciongarante':'','getListadoDatosVendedor'(){const _0x46f1b4=a0_0x3307;axios[_0x46f1b4(0xbe)](_0x46f1b4(0x10f))['then'](_0x26d04e=>{const _0xdbec0f=_0x46f1b4;this['listadoDatos']=_0x26d04e[_0xdbec0f(0xed)][_0xdbec0f(0x117)],this[_0xdbec0f(0x125)][_0xdbec0f(0xdc)](_0x3b7d31=>_0x3b7d31['fecha']=dayjs[_0xdbec0f(0x13e)](_0x3b7d31[_0xdbec0f(0xcf)])[_0xdbec0f(0xc7)](_0xdbec0f(0x150))),this[_0xdbec0f(0x125)][_0xdbec0f(0xdc)](_0x4a4f14=>_0x4a4f14[_0xdbec0f(0x159)]=dayjs[_0xdbec0f(0x13e)](_0x4a4f14[_0xdbec0f(0x159)])['format']('YYYY-MM-DD')),this[_0xdbec0f(0x145)]=this['listadoDatos'],this[_0xdbec0f(0xff)]=_0x26d04e[_0xdbec0f(0xed)][_0xdbec0f(0xff)],this[_0xdbec0f(0xb2)](),this[_0xdbec0f(0x145)]['sort']((_0x3f40ea,_0x70d03d)=>{const _0x3e9e71=_0xdbec0f;let _0x5088d5=_0x3f40ea[_0x3e9e71(0x98)]['toLowerCase'](),_0x332a1e=_0x70d03d['nombre']['toLowerCase']();if(_0x5088d5>_0x332a1e)return 0x1;if(_0x5088d5<_0x332a1e)return-0x1;if(_0x5088d5==_0x332a1e)return 0x0;});});},'getListaItems'(){const _0x3eac28=a0_0x3307;let _0xfb084d=[];this[_0x3eac28(0xff)]==_0x3eac28(0x137)?_0xfb084d=this['listadoDatos'][_0x3eac28(0x128)](_0x9a1ef0=>_0x9a1ef0[_0x3eac28(0x132)]==null)['map'](_0x406309=>_0x406309[_0x3eac28(0xf8)]):_0xfb084d=this[_0x3eac28(0x125)][_0x3eac28(0x128)](_0x44d15f=>_0x44d15f[_0x3eac28(0x132)]==null)['map'](_0x150aec=>_0x150aec['calle']);let _0x12bbf3={};this['listaItemsDatos']=[],_0xfb084d['forEach'](_0x102c6b=>{_0x102c6b in _0x12bbf3?_0x12bbf3[_0x102c6b]+=0x1:_0x12bbf3[_0x102c6b]=0x1;});for(let _0x43596e in _0x12bbf3){this['listaItemsDatos'][_0x3eac28(0x13a)](_0x43596e+'-'+_0x12bbf3[_0x43596e]);}this[_0x3eac28(0xfc)]=this[_0x3eac28(0xfc)][_0x3eac28(0x126)]();},'getListadoArt'(){const _0x4cffcb=a0_0x3307;axios[_0x4cffcb(0xbe)]('/kHEhacFNmI2vflFHBbaT1AQ1Z')[_0x4cffcb(0x130)](_0x3c233e=>{const _0x21a45e=_0x4cffcb;this['Articulos']=_0x3c233e[_0x21a45e(0xed)][_0x21a45e(0xf0)],this[_0x21a45e(0x118)]=this[_0x21a45e(0x157)][_0x21a45e(0xdc)](_0x2ba0ca=>_0x2ba0ca[_0x21a45e(0xef)]);});},'filtraDatosPorVendedor'(_0x222ffd){const _0x14bd80=a0_0x3307;this['listadoDatos_']=this[_0x14bd80(0x125)][_0x14bd80(0x128)](_0x119a33=>_0x119a33[_0x14bd80(0xd1)]==_0x222ffd);},'filtraDatosPorStatus'(_0xf361bd){const _0x14ea2d=a0_0x3307;switch(_0xf361bd){case'vendidos':this[_0x14ea2d(0x145)]=this['listadoDatos'][_0x14ea2d(0x128)](_0x14eee3=>_0x14eee3['resultado']==0x1);break;case _0x14ea2d(0x103):this['listadoDatos_']=this['listadoDatos'][_0x14ea2d(0x128)](_0x29a8ad=>_0x29a8ad[_0x14ea2d(0x132)]==0x0);break;case'pendientes':this[_0x14ea2d(0x145)]=this[_0x14ea2d(0x125)][_0x14ea2d(0x128)](_0x1563ba=>_0x1563ba[_0x14ea2d(0x132)]==null);break;case _0x14ea2d(0xae):this[_0x14ea2d(0x145)]=this[_0x14ea2d(0x125)];break;}},'filtraPorItem'(_0x12de06){const _0x41b608=a0_0x3307;pattern=/[^-]*/gi,_0x12de06=pattern['exec'](_0x12de06),this[_0x41b608(0xff)]==_0x41b608(0x137)?(this[_0x41b608(0x145)]=this[_0x41b608(0x125)][_0x41b608(0x128)](_0x44ade9=>_0x44ade9[_0x41b608(0xf8)]==_0x12de06),this[_0x41b608(0x145)][_0x41b608(0x126)]((_0x4286b4,_0x902a7d)=>{const _0x154596=_0x41b608;let _0x4150ad=_0x4286b4[_0x154596(0x104)][_0x154596(0xc2)](),_0x4b92f8=_0x902a7d[_0x154596(0x104)][_0x154596(0xc2)]();if(_0x4150ad<_0x4b92f8)return-0x1;if(_0x4150ad>_0x4b92f8)return 0x1;return 0x0;})):(this[_0x41b608(0x145)]=this[_0x41b608(0x125)]['filter'](_0x3c8525=>_0x3c8525['calle']==_0x12de06),this['listadoDatos_'][_0x41b608(0x126)]((_0x5f52d3,_0x57ba91)=>_0x5f52d3[_0x41b608(0x97)]-_0x57ba91[_0x41b608(0x97)])),this[_0x41b608(0x12f)]=![];},'abrirCliente'(_0x4a9897){const _0x1a62df=a0_0x3307;idButton=document[_0x1a62df(0xc4)](_0x1a62df(0xdb)),idButton[_0x1a62df(0xba)]=![],idButton=document[_0x1a62df(0xc4)](_0x1a62df(0xdf)),idButton['disabled']=![],idButton=document[_0x1a62df(0xc4)](_0x1a62df(0xac)),idButton[_0x1a62df(0xba)]=![],idButton=document[_0x1a62df(0xc4)](_0x1a62df(0x15c)),idButton[_0x1a62df(0xba)]=![],idButton=document[_0x1a62df(0xc4)]('buttonFallecioDato'),idButton[_0x1a62df(0xba)]=![],this[_0x1a62df(0xe2)]=this['listadoDatos'][_0x1a62df(0x128)](_0x25b111=>_0x25b111['idcliente']==_0x4a9897)[0x0],this[_0x1a62df(0x12f)]=!![];},'editarWapp'(){toggleModal('modal-edicion-wapp');},'guardarWapp'(){const _0x33343b=a0_0x3307;toggleModal('modal-edicion-wapp'),axios[_0x33343b(0xee)][_0x33343b(0x152)][_0x33343b(0x151)]['X-CSRF-TOKEN']=this[_0x33343b(0xec)][_0x33343b(0xaa)][_0x33343b(0xa4)],axios[_0x33343b(0x14d)](_0x33343b(0x10c),this[_0x33343b(0xe2)])[_0x33343b(0x130)](_0x201f43=>{const _0x104258=_0x33343b;msgSuccess(_0x104258(0xe0));})[_0x33343b(0x101)](_0x53f694=>{const _0x4fa8c6=_0x33343b;msgError(_0x4fa8c6(0x114));});},'venderDato'(_0x536417){const _0x5772fd=a0_0x3307;idButton=document[_0x5772fd(0xc4)](_0x5772fd(0x15a)),idButton[_0x5772fd(0xba)]=![],axios[_0x5772fd(0xbe)](_0x5772fd(0x161)+_0x536417)['then'](_0x50c586=>{const _0x30067b=_0x5772fd;this['Dato']=_0x50c586['data'][_0x30067b(0x110)],this[_0x30067b(0xe2)][_0x30067b(0xcf)]=dayjs[_0x30067b(0x13e)](this['Dato']['fecha'])['format'](_0x30067b(0x150)),this[_0x30067b(0xe2)]['fecha_visitar']=dayjs[_0x30067b(0x13e)](this[_0x30067b(0xe2)]['fecha_visitar'])[_0x30067b(0xc7)](_0x30067b(0x150)),this[_0x30067b(0x95)]=[],this[_0x30067b(0xc5)]={'cnt':'','art':'','primera':dayjs[_0x30067b(0x13e)]()[_0x30067b(0xc7)](_0x30067b(0x150)),'dnigarante':this[_0x30067b(0xe2)][_0x30067b(0x10e)]},this[_0x30067b(0xc1)]='',this[_0x30067b(0x14a)]=![],this[_0x30067b(0xe2)][_0x30067b(0x13d)]==0x1&&(this[_0x30067b(0x118)]=this[_0x30067b(0x118)][_0x30067b(0x128)](_0x4aa5f1=>!_0x4aa5f1[_0x30067b(0xd0)](_0x30067b(0xc9)))),toggleModal(_0x30067b(0xb4));});},'anularDato'(_0x3c8541){const _0x237e33=a0_0x3307;idButton=document[_0x237e33(0xc4)]('buttonAnularDato'),idButton[_0x237e33(0xba)]=!![],axios['get'](_0x237e33(0x116)+_0x3c8541)['then'](_0x48b2a3=>{const _0x161a5e=_0x237e33;msgSuccess(_0x161a5e(0xfb)),this[_0x161a5e(0x143)](),this[_0x161a5e(0x12f)]=![];})[_0x237e33(0x101)](_0x430c8e=>{const _0x167249=_0x237e33;msgError(_0x167249(0xbc));});},'mudoDato'(_0x42d6c5){const _0xa5046d=a0_0x3307;Swal[_0xa5046d(0x129)]({'title':_0xa5046d(0xfa),'text':_0xa5046d(0xca),'icon':_0xa5046d(0xab),'showCancelButton':!![],'confirmButtonColor':'#3085d6','cancelButtonColor':_0xa5046d(0x122),'confirmButtonText':_0xa5046d(0xf2)})[_0xa5046d(0x130)](_0x47e0db=>{const _0xb9cc3d=_0xa5046d;_0x47e0db['isConfirmed']&&(idButton=document[_0xb9cc3d(0xc4)](_0xb9cc3d(0x15c)),idButton[_0xb9cc3d(0xba)]=!![],axios[_0xb9cc3d(0xbe)]('/gJUmonE8slTFGZqSKXSVwqPJ1/'+_0x42d6c5)[_0xb9cc3d(0x130)](_0x445730=>{const _0x5eeb4c=_0xb9cc3d;msgSuccess('Dato\x20informado\x20correctamente'),this['getListadoDatosVendedor'](),this[_0x5eeb4c(0x12f)]=![];})[_0xb9cc3d(0x101)](_0x2ebcde=>{const _0x23ca42=_0xb9cc3d;msgError(_0x23ca42(0xd6));}));});},'fallecioDato'(_0x15c6a1){const _0x5c29f4=a0_0x3307;Swal['fire']({'title':_0x5c29f4(0xfa),'text':_0x5c29f4(0x154),'icon':_0x5c29f4(0xab),'showCancelButton':!![],'confirmButtonColor':_0x5c29f4(0x13b),'cancelButtonColor':_0x5c29f4(0x122),'confirmButtonText':_0x5c29f4(0xf2)})[_0x5c29f4(0x130)](_0x4b5134=>{const _0x1e36b9=_0x5c29f4;_0x4b5134[_0x1e36b9(0xe3)]&&(idButton=document[_0x1e36b9(0xc4)](_0x1e36b9(0x131)),idButton[_0x1e36b9(0xba)]=!![],axios[_0x1e36b9(0xbe)]('/sLTFCMArYAdVsrEgwsz7utyRi/'+_0x15c6a1)['then'](_0x53b290=>{const _0x110627=_0x1e36b9;msgSuccess(_0x110627(0xa9)),this[_0x110627(0x143)](),this[_0x110627(0x12f)]=![];})[_0x1e36b9(0x101)](_0x6bbc8b=>{msgError('Hubo\x20un\x20error.\x20El\x20dato\x20no\x20se\x20pudo\x20procesar');}));});},'fecharDato'(_0x1a3843){const _0x57e467=a0_0x3307;idButton=document['getElementById'](_0x57e467(0xdf)),idButton[_0x57e467(0xba)]=!![],toggleModal(_0x57e467(0x11c)),this['verCard']=![];},'guardarDatoFechado'(){const _0x47b702=a0_0x3307;toggleModal(_0x47b702(0x11c)),axios[_0x47b702(0xee)]['headers']['common']['X-CSRF-TOKEN']=this[_0x47b702(0xec)][_0x47b702(0xaa)][_0x47b702(0xa4)],axios[_0x47b702(0x14d)]('/HvjJNtFgF71pRYafzcTC74nUt',this[_0x47b702(0xe2)])['then'](_0x30ad98=>{const _0x5bd3c2=_0x47b702;msgSuccess(_0x5bd3c2(0xb6));})[_0x47b702(0x101)](_0x397af9=>{const _0x90b7a5=_0x47b702;msgError(_0x90b7a5(0xf9));});},'noEstabaDato'(_0x4b03b9){const _0x461450=a0_0x3307;idButton=document['getElementById'](_0x461450(0xac)),idButton[_0x461450(0xba)]=!![],axios[_0x461450(0xbe)](_0x461450(0xa1)+_0x4b03b9),this[_0x461450(0x12f)]=![];},'validarDni'(_0x217057){const _0x2deb79=a0_0x3307;datos={'dni':_0x217057,'id':this[_0x2deb79(0xe2)][_0x2deb79(0x133)]};if(_0x217057==undefined){console[_0x2deb79(0x11d)]('dni\x20inexistente');return;}console[_0x2deb79(0x11d)](datos),axios['defaults']['headers'][_0x2deb79(0x151)][_0x2deb79(0xfe)]=this[_0x2deb79(0xec)]['token']['value'],axios[_0x2deb79(0x14d)](_0x2deb79(0x9e),datos)[_0x2deb79(0x130)](_0x48d9cf=>{this['dnivalidado']=!![];})[_0x2deb79(0x101)](_0x1a0e57=>{const _0x53dadb=_0x2deb79;this[_0x53dadb(0x14c)]=![],msgError('el\x20DNI\x20ingresado\x20no\x20corresponde\x20al\x20cliente');});},'agregarArticulo'(_0x2dfab4,_0x2735f0){const _0x269caa=a0_0x3307;if(_0x2dfab4!=''&&_0x2735f0!=''){let _0x6441eb=this[_0x269caa(0x157)][_0x269caa(0x128)](_0x446195=>_0x446195[_0x269caa(0xef)]==_0x2735f0)[0x0][_0x269caa(0x146)],_0x3dd863=0x6,_0x321c58=_0x2dfab4*_0x6441eb*_0x3dd863,_0x330682=this[_0x269caa(0x95)][_0x269caa(0x9b)];this['listaArtComprados'][_0x269caa(0x13a)]({'id':_0x330682,'cnt':_0x2dfab4,'art':_0x2735f0,'cc':_0x3dd863,'cuota':_0x6441eb,'total':_0x321c58}),this['Venta'][_0x269caa(0xa7)]='',this['Venta']['art']='',this[_0x269caa(0xc1)]=this['listaArtComprados'][_0x269caa(0xdc)](_0x377b72=>_0x377b72[_0x269caa(0x127)])[_0x269caa(0xbd)]((_0x181e5d,_0x438803)=>_0x181e5d+_0x438803,0x0)/0x6;}},'borrarItem'(_0x27fc31){const _0x3c9418=a0_0x3307;let _0x1fa5bc=this[_0x3c9418(0x95)][_0x3c9418(0xdc)](_0xdd6704=>_0xdd6704['id']);idBorrar=_0x1fa5bc[_0x3c9418(0xe1)](_0x27fc31),this[_0x3c9418(0x95)][_0x3c9418(0xa8)](idBorrar,0x1),this['sumaCuota']=this[_0x3c9418(0x95)][_0x3c9418(0xdc)](_0x50fb31=>_0x50fb31['total'])['reduce']((_0xd3aad4,_0x19c33e)=>_0xd3aad4+_0x19c33e,0x0)/0x6;},'pedirAutorizacion'(){const _0x1292c4=a0_0x3307;this[_0x1292c4(0x14a)]=!![],this[_0x1292c4(0xe2)][_0x1292c4(0x9c)]=this[_0x1292c4(0xc1)];let _0x163873=[];this['listaArtComprados'][_0x1292c4(0xdc)](_0x52e0ca=>{const _0x2db78b=_0x1292c4;_0x163873['push'](_0x52e0ca['cnt']+'\x20'+_0x52e0ca[_0x2db78b(0xef)]);}),this[_0x1292c4(0xe2)][_0x1292c4(0x14e)]=_0x163873['toString'](),axios[_0x1292c4(0xee)]['headers'][_0x1292c4(0x151)][_0x1292c4(0xfe)]=this[_0x1292c4(0xec)][_0x1292c4(0xaa)]['value'],axios['post'](_0x1292c4(0xd7),this[_0x1292c4(0xe2)])[_0x1292c4(0x130)](_0x35d459=>{const _0x39982b=_0x1292c4;this[_0x39982b(0xe2)][_0x39982b(0xc0)]=_0x35d459[_0x39982b(0xed)][_0x39982b(0xc0)];});let _0x4c9be6=_0x1292c4(0x135)+this[_0x1292c4(0xe2)][_0x1292c4(0x98)]+_0x1292c4(0x100)+this['Dato'][_0x1292c4(0x14e)]+'\x0ay\x20una\x20cuota\x20de\x20$'+this['sumaCuota']+_0x1292c4(0xd3),_0xec3cbc=_0x1292c4(0xb8),_0x133c48={'msg':_0x4c9be6,'tipo':_0xec3cbc};axios[_0x1292c4(0xee)][_0x1292c4(0x152)][_0x1292c4(0x151)][_0x1292c4(0xfe)]=this[_0x1292c4(0xec)][_0x1292c4(0xaa)][_0x1292c4(0xa4)],axios[_0x1292c4(0x14d)](_0x1292c4(0x96),_0x133c48)['then'](_0x376fbf=>{let _0x1ff0b0=0x0,_0x83a34d=setInterval(()=>{const _0xc20eed=a0_0x3307;axios[_0xc20eed(0xbe)](_0xc20eed(0xc8)+this['Dato'][_0xc20eed(0xc0)])['then'](_0x16d1a5=>{const _0x579e7f=_0xc20eed;_0x1ff0b0=_0x16d1a5['data'][_0x579e7f(0xa6)];if(_0x1ff0b0==0x1){msgDelay(_0x579e7f(0x11b),0x493e0),clearTimeout(_0x83a34d);let _0x94630c=setInterval(()=>{const _0x2e2562=_0x579e7f;axios[_0x2e2562(0xbe)](_0x2e2562(0x113)+this['Dato'][_0x2e2562(0xc0)])[_0x2e2562(0x130)](_0xcfbe88=>{const _0x41bdd8=_0x2e2562;switch(_0xcfbe88[_0x41bdd8(0xed)][_0x41bdd8(0x9a)]){case _0x41bdd8(0x107):msgSuccess('Aprobado',_0x41bdd8(0x155),0x2710),clearTimeout(_0x94630c),setTimeout(()=>{const _0x54d401=_0x41bdd8;window[_0x54d401(0xb0)]=_0x54d401(0x12c);},0x2774);break;case'sigueigual':msgWarning(_0x41bdd8(0x15f),_0x41bdd8(0xce),0x2710),clearTimeout(_0x94630c),setTimeout(()=>{const _0x29307e=_0x41bdd8;window['location']=_0x29307e(0x12c);},0x2774);break;case _0x41bdd8(0xc3):msgError(_0x41bdd8(0xd9),_0x41bdd8(0xf5),0x2710),clearTimeout(_0x94630c),setTimeout(()=>{const _0x3954c7=_0x41bdd8;window[_0x3954c7(0xb0)]=_0x3954c7(0x12c);},0x2774);break;}});},0x2710);}});},0x2710);});},'pasarVenta'(){const _0x572c66=a0_0x3307;if(this['dnivalidado']==![]){msgError(_0x572c66(0x94));return;}if(this[_0x572c66(0x95)][_0x572c66(0x9b)]==0x0){msgError('Debe\x20agregar\x20articulos\x20comprados');return;}if(!dayjs(this[_0x572c66(0xc5)][_0x572c66(0xe6)])['isAfter'](dayjs[_0x572c66(0x13e)]())){msgError(_0x572c66(0x105));return;}if(this[_0x572c66(0xc1)]>this['Dato'][_0x572c66(0xb5)]){msgError('La\x20venta\x20excede\x20la\x20cuota\x20maxima\x20aprobada');return;}idButton=document['getElementById'](_0x572c66(0x15a)),idButton[_0x572c66(0xba)]=!![],this[_0x572c66(0xe2)][_0x572c66(0x14e)]=this[_0x572c66(0x95)],this[_0x572c66(0xe2)][_0x572c66(0xe6)]=this[_0x572c66(0xc5)][_0x572c66(0xe6)],this[_0x572c66(0xe2)][_0x572c66(0x146)]=this['sumaCuota'],axios[_0x572c66(0xee)][_0x572c66(0x152)][_0x572c66(0x151)]['X-CSRF-TOKEN']=this[_0x572c66(0xec)][_0x572c66(0xaa)]['value'],axios[_0x572c66(0x14d)](_0x572c66(0x153),this[_0x572c66(0xe2)])[_0x572c66(0x130)](_0x234f53=>{const _0x24ec18=_0x572c66;this[_0x24ec18(0x143)](),msgSuccess(_0x24ec18(0x158)),toggleModal(_0x24ec18(0xb4)),axios[_0x24ec18(0xbe)](_0x24ec18(0x161)+this[_0x24ec18(0xe2)]['id'])[_0x24ec18(0x130)](_0x4edbe=>{const _0x5ca89f=_0x24ec18;this[_0x5ca89f(0xe2)]=_0x4edbe['data'][_0x5ca89f(0x110)],this[_0x5ca89f(0xe2)][_0x5ca89f(0xcf)]=dayjs[_0x5ca89f(0x13e)](this[_0x5ca89f(0xe2)][_0x5ca89f(0xcf)])[_0x5ca89f(0xc7)](_0x5ca89f(0x150)),this[_0x5ca89f(0xe2)][_0x5ca89f(0x159)]=dayjs['utc'](this['Dato']['fecha_visitar'])['format']('YYYY-MM-DD'),this[_0x5ca89f(0x119)](this[_0x5ca89f(0xe2)]);});})['catch'](_0x17de6c=>{const _0x4d71be=_0x572c66;msgError(_0x4d71be(0x15d));});},'hacerLlamada'(_0x46d9db){const _0x39a2d0=a0_0x3307;re=/[0-9]*/,_0x46d9db=re[_0x39a2d0(0xcc)](_0x46d9db)[0x0],window['location'][_0x39a2d0(0xf1)]='tel:'+_0x46d9db;},'buscaGarante'(_0x3d7aad){const _0x13d720=a0_0x3307;this[_0x13d720(0xc5)][_0x13d720(0x10e)]!=0x0&&this[_0x13d720(0xc5)][_0x13d720(0x10e)]!=''?axios['get'](_0x13d720(0xd8)+this['Venta']['dnigarante'])[_0x13d720(0x130)](_0x29ca46=>{const _0x43fcfb=_0x13d720;this[_0x43fcfb(0xcb)]=_0x29ca46[_0x43fcfb(0xed)][_0x43fcfb(0xc6)][0x0][_0x43fcfb(0x98)],this['dnigarantevalidado']=!![];})['catch'](_0x327787=>{const _0x1086c0=_0x13d720;msgError(_0x1086c0(0x102)),this['dnigarantevalidado']=![];}):this[_0x13d720(0xcb)]='';},'enviarWappCliente'(_0x33a4b4){const _0x35f0dc=a0_0x3307;let _0x5f09d4='',_0x58bce2;for(let _0x5b9270 of this[_0x35f0dc(0x95)]){_0x5f09d4+='\x20'+_0x5b9270[_0x35f0dc(0xa7)]+'\x20'+_0x5b9270[_0x35f0dc(0xef)]+'\x20',_0x58bce2=_0x5b9270['cc'];}let _0x10cc68=_0x35f0dc(0x111)+_0x33a4b4['nombre']+_0x35f0dc(0xeb)+_0x5f09d4+_0x35f0dc(0xe8)+_0x58bce2+_0x35f0dc(0xf4)+_0x33a4b4['monto_vendido']/_0x58bce2+_0x35f0dc(0x106)+this[_0x35f0dc(0xc5)][_0x35f0dc(0xe6)]+_0x35f0dc(0x10b),_0x579314=_0x33a4b4[_0x35f0dc(0x142)],_0x3285a4=_0x33a4b4[_0x35f0dc(0x133)],_0x250727=_0x35f0dc(0xe7),_0x13c984={'msg':_0x10cc68,'wapp':_0x579314,'idcliente':_0x3285a4,'file':_0x250727};axios['defaults'][_0x35f0dc(0x152)][_0x35f0dc(0x151)][_0x35f0dc(0xfe)]=this[_0x35f0dc(0xec)][_0x35f0dc(0xaa)][_0x35f0dc(0xa4)],axios[_0x35f0dc(0x14d)](_0x35f0dc(0xf3),_0x13c984)[_0x35f0dc(0x130)](_0x5daf05=>{const _0x4253ab=_0x35f0dc;axios['post'](_0x4253ab(0xbf),_0x13c984);});}};}function GnIVzsHTcsg1sQFsVD7xfw7Dc(){return{'listaArtVendedor':[],'getArtVendedor'(){const _0x11a23b=a0_0x3307;axios['get'](_0x11a23b(0xb1))[_0x11a23b(0x130)](_0x378def=>{const _0x22474e=_0x11a23b;this[_0x22474e(0x123)]=_0x378def[_0x22474e(0xed)][_0x22474e(0x156)];});}};}function IkKmqwFGcDGnhd8x1TvBO6C6p(){return{'listaComisiones':[],'listaComisiones_':[],'totalComision':'','listaFechas':[],'fecha':'','getComisionesVdor'(){const _0x5ede29=a0_0x3307;axios[_0x5ede29(0xbe)]('/IrV7gmqz4Wu8Q8rwmXMftphaB')[_0x5ede29(0x130)](_0x2d4a74=>{const _0x5ef6db=_0x5ede29;this[_0x5ef6db(0x144)]=_0x2d4a74['data']['comisiones'],this[_0x5ef6db(0x144)][_0x5ef6db(0xdc)](_0x5da924=>_0x5da924['fecha']=dayjs['utc'](_0x5da924[_0x5ef6db(0xcf)])[_0x5ef6db(0xc7)](_0x5ef6db(0x150))),this[_0x5ef6db(0x144)]['map'](_0xa67b02=>_0xa67b02['com']=parseFloat(_0xa67b02[_0x5ef6db(0xa0)])),this['totalComision']=parseFloat(this[_0x5ef6db(0x144)][_0x5ef6db(0xdc)](_0x37fc9f=>_0x37fc9f[_0x5ef6db(0xa0)])[_0x5ef6db(0xbd)]((_0x3cd8c5,_0x53b501)=>_0x3cd8c5+_0x53b501,0x0)),this[_0x5ef6db(0x140)]=_0x2d4a74['data'][_0x5ef6db(0xf7)],this[_0x5ef6db(0x140)][_0x5ef6db(0xdc)](_0x592742=>_0x592742[_0x5ef6db(0xcf)]=dayjs[_0x5ef6db(0x13e)](_0x592742['fecha'])['format']('YYYY-MM-DD')),this[_0x5ef6db(0x140)][_0x5ef6db(0xdc)](_0x3c219=>_0x3c219[_0x5ef6db(0x148)]=parseFloat(_0x3c219[_0x5ef6db(0x148)]));});},'expandChildren'(_0x1eeea8){const _0x2e8b3f=a0_0x3307;if(this[_0x2e8b3f(0xcf)]==_0x1eeea8&&this[_0x2e8b3f(0x138)][_0x2e8b3f(0x9b)]>0x0){this[_0x2e8b3f(0x138)]=[];return;}this['listaComisiones_']=this['listaComisiones'][_0x2e8b3f(0x128)](_0x561dc1=>_0x561dc1['fecha']==_0x1eeea8),this[_0x2e8b3f(0xcf)]=_0x1eeea8,setTimeout(()=>{const _0x2ff4de=_0x2e8b3f;$tbody=document[_0x2ff4de(0xe9)](_0x2ff4de(0xda)),$trfecha=document['getElementById'](_0x1eeea8);let _0x40eafb=Array[_0x2ff4de(0x109)]($tbody['children']),_0x138a94=_0x40eafb[_0x2ff4de(0x128)](_0x2db3b9=>_0x2db3b9[_0x2ff4de(0xaf)]['contains'](_0x2ff4de(0xad)));_0x138a94=_0x138a94[_0x2ff4de(0xd4)]();for(el of _0x138a94){$tbody['insertBefore'](el,$trfecha[_0x2ff4de(0xbb)]);}},0xa);},'avisarRetiroZona'(){const _0x3c6b90=a0_0x3307;idButton=document[_0x3c6b90(0xc4)](_0x3c6b90(0x13c)),idButton[_0x3c6b90(0xba)]=!![],msgDelay(_0x3c6b90(0x14b));let _0x46db3e=_0x3c6b90(0x147),_0x1aab8c=_0x3c6b90(0xdd),_0x5ba715={'msg':_0x46db3e,'tipo':_0x1aab8c};axios['defaults'][_0x3c6b90(0x152)][_0x3c6b90(0x151)][_0x3c6b90(0xfe)]=this['$refs'][_0x3c6b90(0xaa)]['value'],axios[_0x3c6b90(0x14d)]('/3ZbXanrRQalY6JL5eOBi49Nyc',_0x5ba715)[_0x3c6b90(0x130)](_0x1a9544=>{const _0x530f12=_0x3c6b90;msgSuccess(_0x530f12(0xb3));});}};}function a0_0x36a0(){const _0x465e00=['fire','3365290NmSQqE','Debe\x20ingresar\x20el\x20DNI','/2xxXix5cnz7IKcYegqs6qf0R6','listaVisitasVendedor','45uFxrUS','verCard','then','buttonFallecioDato','resultado','idcliente','24248athQTp','Solicito\x20autorizacion\x20para\x20','151418xeCkvt','zonas','listaComisiones_','barrios','push','#3085d6','buttonRetiroZona','nosabana','utc','/MeHzAqFYsbb78KAVFAGTlZRW9/','listaFechas','pedirAutorizacion','wapp','getListadoDatosVendedor','listaComisiones','listadoDatos_','cuota','Retiro\x20zona.','comision','listaVisitasVendedor_','verNotificacionAutorizacion','se\x20estan\x20enviando\x20los\x20mensajes...','dnivalidado','post','arts','Debe\x20ingresar\x20el\x20numero\x20de\x20la\x20casa','YYYY-MM-DD','common','headers','/xuNzBi4bvtSugd5KbxSQzD0Ey','Se\x20pondra\x20como\x20fallecido\x20el\x20dato','El\x20dato\x20fue\x20autorizado','artvendedor','Articulos','Venta\x20pasada\x20con\x20exito','fecha_visitar','buttonPasarVenta','Este\x20cliente\x20ya\x20tiene\x20un\x20dato\x20hecho\x20y\x20esta\x20asignado\x20a\x20otro\x20vendedor.','buttonMudoDato','Hubo\x20un\x20error\x20y\x20la\x20venta\x20no\x20se\x20proceso.','Aprobado','La\x20cuota\x20fue\x20rechazada','cliente','/pnZWxv9Nicwt6TQ6zxohzvats/','El\x20DNI\x20del\x20cliente\x20debe\x20coincidir\x20con\x20nuestros\x20registros','listaArtComprados','/3ZbXanrRQalY6JL5eOBi49Nyc','num','nombre','/pEmPj7NAUn0Odsru4aL2BhlOu','respuesta','length','cuota_requerida','/CZI6X7BC6wNtseAN22HiXsmqc','/fc3vpQG6SzEH95Ya7kTJPZ48M','insertBefore','com','/G9S85pbqWVEX17nNQuOOnpxvn/','2784678SMMDav','calles','value','dni','tomado','cnt','splice','Dato\x20informado\x20correctamente','token','warning','buttonNoestabaDato','children','todos','classList','location','/k8E5hsVs4be3jsJJaob6OQmAX','getListaItems','Avisado\x20retiro\x20zona.','modal-pasar-venta','cuota_maxima','Dato\x20fechado\x20con\x20exito','fechasvisitas','autorizacion\x20venta','768jvgKBq','disabled','nextSibling','Hubo\x20un\x20error.\x20El\x20dato\x20no\x20se\x20pudo\x20anular','reduce','get','/4qUK6eNZnCYjIiGTt3HSj2YDp','idautorizacion','sumaCuota','toLowerCase','rechazado','getElementById','Venta','garante','format','/u0IEJT3i1INZpKoNKbyezlfRy/','Sab','Se\x20pondra\x20como\x20mudado\x20el\x20dato','nombregarante','exec','direcciongarante','La\x20cuota\x20no\x20fue\x20autorizada.\x20Se\x20puede\x20vender\x20hasta\x20la\x20cuota\x20maxima\x20que\x20tenia\x20antes.','fecha','includes','vendedor','result','.\x0aQuedo\x20a\x20la\x20espera.\x20Gracias.','reverse','listaFechas_','Hubo\x20un\x20error.\x20El\x20dato\x20no\x20se\x20pudo\x20procesar','/vaHQ2gFYLW2pIWSr5I0ogCL0k','/3ibzPLLq53RuFgIqkq6G3bSzO/','Rechazado','tbody','buttonAnularDato','map','retiro\x20zona','756339Hvomxt','buttonFecharDato','WhatsApp\x20editado\x20correctamente','indexOf','Dato','isConfirmed','visitasvendedor','pedido-autorizacion','primera','informacion-importante','.\x0aLe\x20recordamos\x20que\x20el\x20plan\x20de\x20pagos\x20elegido\x20es\x20de\x20','querySelector','1939668cchWeb',',\x20agradecemos\x20su\x20compra\x20de\x20','$refs','data','defaults','art','articulos','href','Si,\x20ponerlo!','/hX53695XAOpaLY9itLgmghkhH','\x20cuotas\x20mensuales\x20de\x20$','El\x20dato\x20ha\x20sido\x20rechazado.\x20No\x20se\x20le\x20puede\x20vender','Debe\x20ingresar\x20los\x20articulos\x20que\x20va\x20a\x20vender','fechascomisiones','zona','Hubo\x20un\x20error.\x20El\x20dato\x20no\x20se\x20fecho','¿Esta\x20seguro?','Dato\x20anulado\x20correctamente','listaItemsDatos','vdor','X-CSRF-TOKEN','agrupar','\x0acon\x20una\x20compra\x20de\x20','catch','El\x20DNI\x20no\x20existe','anulados','calle','La\x20fecha\x20de\x20primer\x20cuota\x20debe\x20ser\x20posterior\x20a\x20hoy','\x20y\x20la\x20primer\x20cuota\x20vence\x20el\x20dia\x20','autorizado','1735005pNErDi','from','contains','\x20para\x20cualquier\x20consulta\x20no\x20dude\x20en\x20contactarnos,\x20estamos\x20a\x20su\x20disposición!.','/uQ3gisetQ8v0n6tw81ORnpL1s','direccion','dnigarante','/VGIdj7tUnI1hWCX3N7W7WAXgU','dato','Estimado\x20cliente:\x20','Verifique\x20que\x20ingreso\x20una\x20calle\x20correcta','/ymIVWKdjgnCeJvo2zcodwRTQM/','Error.\x20No\x20se\x20hizo\x20la\x20edicion','otroasignado','/UtVc3f6y5hfxu2dPmcrV9Y7mc/','listadodatos','listaArticulos','enviarWappCliente','Verifique\x20que\x20ingreso\x20un\x20barrio\x20correcto','la\x20autorizacion\x20se\x20esta\x20procesando.\x20Puede\x20tardar\x20un\x20poco...','modal-fechar-dato','log','/F8cq9GzHJIG9hENBo0Xq7hdH7','/w98LuAaWBax9c6rENQ2TjO3PR','2UOrgOB','Debe\x20ingresar\x20la\x20cuota\x20que\x20va\x20a\x20vender','#d33','listaArtVendedor','Cliente\x20existente','listadoDatos','sort','total','filter'];a0_0x36a0=function(){return _0x465e00;};return a0_0x36a0();}