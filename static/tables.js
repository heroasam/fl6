let listaheads = document.querySelectorAll('thead');
$theads = Array.from(listaheads)
$theads.forEach($thead=>{
    let heads = $thead.children.length
    if(heads===3) {
    $thead.removeChild($thead.lastElementChild)
    $thead.removeChild($thead.firstElementChild)
    heads = $thead.children.length
    }
})


//removemos el tr de fecha que complica y afea el encabezado
// let factor;
// switch (heads) {
//     case 1:
//         factor=1;
//         break;
//     case 2:
//         factor=2;
//         break;
//     case 3:
//         factor=2;
//         break;
//     default:
//         factor=0;
//         break
// }
function nop(pesos){
  let signo = pesos.substr(0,1)
  if (signo=="$"){
    let len =  pesos.length - 1
    let valor = pesos.substr(1,len)
    return valor
  }else{
    return pesos
  }
};
const totalizar = (tableId)=>{
        let tbody = tableId.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let rowIndex=[];
        rowsArray.forEach((row)=>{
            if(row.classList.contains('selected')) {
                rowIndex.push(row.rowIndex-1)
                //hago factor 1 pq se eliminan las filas sobrantes y se deja 1
                //console.log(row);
            }
        });
        let maxRow = Math.max(...rowIndex)+1;
        let $rowTotal = tbody.insertRow(maxRow);
        let $cell0 = $rowTotal.insertCell(0);
        $cell0.innerHTML = "SubTotal";
        $rowTotal.classList.add('subtotal');
        //console.log($rowTotal)

        const cols = rowsArray[0].children.length // determino la cant columnas
        for(let i=1;i<cols;i++){
        let col = [];
        rowIndex.forEach((ix)=>{
            col.push(nop(tbody.rows[ix].cells[i].innerText))
        });
        let total = col.reduce((a,b)=>Number(a)+Number(b));
        let $cell = $rowTotal.insertCell(i);
        if (!(Number.isNaN(total))) $cell.innerHTML = total
        }

    };

const restaurar = (tableId)=>{
        let tbody = tableId.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let rowtotal=[];
        rowsArray.forEach((row)=>{
            if(row.classList.contains('selected')) {
                row.classList.remove('selected');
            }
        });
        let $rowSubTotal = document.querySelectorAll('.subtotal');
        $rowSubTotal.forEach((row)=>{
            row.remove();
        })
    };

const markSelected = (only=0)=>{
        if (event.target.parentElement.parentElement.tagName!='TBODY') return;
        const $row = event.target.parentElement;
        if(only===0) {
        $row.classList.remove('selected');
        }else{
        $row.classList.add('selected');
        }
}

const sortGrid = (colNum,dir)=>{
        let tbody = table.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let compare;
        let compareAsc;
        compareAsc = function(rowA, rowB) {
            return (rowA.cells[colNum].innerHTML).localeCompare(rowB.cells[colNum].innerHTML);
        }
        let compareDesc;
        compareDesc = function(rowA, rowB) {
            return (rowA.cells[colNum].innerHTML).localeCompare(rowB.cells[colNum].innerHTML)*-1;
        }
        if (dir==='ASC') {
            compare = compareAsc;
        } else {
            compare = compareDesc;
        }
        rowsArray.sort(compare);
        tbody.append(...rowsArray);
}

const sortGridNumerica = (colNum,dir)=>{
        let tbody = table.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let compare;
        let compareAsc;
        compareAsc = function(rowA, rowB) {
           return rowA.cells[colNum].innerHTML - rowB.cells[colNum].innerHTML;
        }
        let compareDesc;
        compareDesc = function(rowA, rowB) {
            return rowB.cells[colNum].innerHTML - rowA.cells[colNum].innerHTML;
        }
        if (dir==='ASC') {
            compare = compareAsc;
        } else {
            compare = compareDesc;
        }
        rowsArray.sort(compare);
        tbody.append(...rowsArray);
}

document.addEventListener('click', ()=>{
    if(event.target.tagName=== 'TH'){
        let th = event.target;
        sortGrid(th.cellIndex,'ASC')
    }
    if(event.target.tagName=== 'TH' && event.ctrlKey===true){
        let th = event.target;
        sortGridNumerica(th.cellIndex,'ASC')
    }

    });

document.addEventListener('click', ()=>{
    if(!event.target.parentElement.parentElement.parentElement.classList.contains('nototal')){
        // este if condiciona a que la tabla no tenga la clase nototal
        // o sea la funcion seleccionar y totalizar etc. funcionan con tablas sin la clase nototal
        if(event.target.tagName==='TD') {
            markSelected(1)
        };
        if(event.target.tagName=== 'TD' && event.ctrlKey===true){
            t=event.target.parentElement.parentElement.parentElement
            totalizar(t)
        };
    }
})



document.addEventListener('mousedown',()=>{
    if(event.target.tagName==='TD') event.preventDefault();
    if(event.target.tagName==='TH') event.preventDefault();
    // prevenimos la accion de seleccionar valores
    // de la tabla que es molesto y no sirve para nada.
});

document.addEventListener('mouseover',()=>{
        if(event.target.tagName==='TD') {
            if(!event.target.parentElement.parentElement.parentElement.classList.contains('nototal')){
            // este if condiciona a que la tabla no tenga la clase nototal
            // o sea la funcion seleccionar y totalizar etc. funcionan con tablas sin la clase nototal
                if(event.buttons===1){
                markSelected(1)
                }
            }
        };
    })


document.addEventListener('contextmenu', ()=>{
        // sort tabla por columnas con boton derecho en el encabezado
        event.preventDefault()
        // prevenDefault para que no funcione como esta predeterminado
        if(event.target.tagName=== 'TD'){
            t=event.target.parentElement.parentElement.parentElement
            restaurar(t)
        };
        // el event.target entrega el elemento clickado, si su tagName es TD
        // buscampos el parent del parent del parent que es la tabla
        // y lanzamos la funcion restaurar(tabla)
        if(event.target.tagName!= 'TH') return;
        // luego si no es un TH terminamos
        if(event.target.tagName=== 'TH') {
        let th = event.target;
        sortGrid(th.cellIndex,'DESC')
        }
        // si es un TH lanzamos la funcion sortGrid 
        if(event.target.tagName=== 'TH' && event.ctrlKey===true) {
            let th = event.target;
            sortGridNumerica(th.cellIndex,'DESC')
            }
        // si es un TH con la tecla ctrl presionada lanzamos la funcion
        // sortGridNumerica
        
    });

// document.addEventListener('keydown',(e)=>{
//         t=e.target.parentElement.parentElement.parentElement
//         switch (e.key) {
//             case 't' : {
//                 totalizar(t)
//                 break
//             };
//             case 'r': {
//                 restaurar(t)
//                 break
//             }
//         };
//     })
