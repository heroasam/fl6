let listaheads = document.querySelectorAll('thead');
$theads = Array.from(listaheads);
$theads.forEach($thead=>{
    let heads = $thead.children.length;
    if(heads===3) {
	$thead.removeChild($thead.lastElementChild);
	$thead.removeChild($thead.firstElementChild);
	heads = $thead.children.length;
    }
});

function nop(pesos){
    let signo = pesos.substr(0,1);
  if (signo=="$"){
      let len =  pesos.length - 1;
      let valor = pesos.substr(1,len);
      return valor;
  }else{
      return pesos;
  }
};

const totalizar = (tableId)=>{
        let tbody = tableId.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let rowIndex=[];
        rowsArray.forEach((row)=>{
            if(row.classList.contains('is-selected')) {
                rowIndex.push(row.rowIndex-1);
                //hago factor 1 pq se eliminan las filas sobrantes y se deja 1
            }
        });
        let maxRow = Math.max(...rowIndex)+1;
        let $rowTotal = tbody.insertRow(maxRow);
        $rowTotal.classList.add('subtotal');

    const cols = rowsArray[0].children.length; // determino la cant columnas
    for (let i=0;i<cols;i++){
        $rowTotal.insertCell(i);
    }
    $rowTotal.cells[0].innerHTML = "Subtotal";

    const $ths = document.querySelectorAll('th');
    const $thtotal = [];
    const $thclass = [];
    Array.from($ths).forEach(th=>
        {if(th.classList.contains('sumar')){
            $thtotal.push(th.cellIndex);
            $thclass.push(Array.from(rowsArray[0].cells[th.cellIndex].classList));
        }});
    console.log($thclass);

        for(let index in $thtotal){
            let i = parseInt($thtotal[index]);
        let col = [];
        rowIndex.forEach((ix)=>{
            col.push(nop(tbody.rows[ix].cells[i].innerText));
        });
        let total = col.reduce((a,b)=>Number(a)+Number(b),0);
        let $cell = $rowTotal.cells[i];
            console.log(...$thclass[index]);
            $cell.classList.add(...$thclass[index]);
            if (!(Number.isNaN(total))) $cell.innerHTML = total;
        }

    };

const restaurar = (tableId)=>{
        let tbody = tableId.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let rowtotal=[];
        rowsArray.forEach((row)=>{
            if(row.classList.contains('is-selected')) {
                row.classList.remove('is-selected');
            }
        });
        let $rowSubTotal = document.querySelectorAll('.subtotal');
        $rowSubTotal.forEach((row)=>{
            row.remove();
        });
    };


// markSelected es un toggle que selecciona/deselecciona
const markSelected = (forma=null)=>{
    if (event.target.parentElement.parentElement.tagName!='TBODY') return;
    const $row = event.target.parentElement;
    if(forma=='add') {
	$row.classList.add('is-selected');
    }else{
	if($row.classList.contains('is-selected')) {
	    $row.classList.remove('is-selected');
	}else{
	    $row.classList.add('is-selected');
	}
    }
};


const sortGrid = (colNum,dir)=>{
        let tbody = table.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let compare;
        let compareAsc;
        compareAsc = function(rowA, rowB) {
            return (rowA.cells[colNum].innerHTML).localeCompare(rowB.cells[colNum].innerHTML);
        };
        let compareDesc;
        compareDesc = function(rowA, rowB) {
            return (rowA.cells[colNum].innerHTML).localeCompare(rowB.cells[colNum].innerHTML)*-1;
        };
        if (dir==='ASC') {
            compare = compareAsc;
        } else {
            compare = compareDesc;
        }
        rowsArray.sort(compare);
        tbody.append(...rowsArray);
};


const sortGridNumerica = (colNum,dir)=>{
        let tbody = table.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let compare;
        let compareAsc;
        compareAsc = function(rowA, rowB) {
           return rowA.cells[colNum].innerHTML - rowB.cells[colNum].innerHTML;
        };
        let compareDesc;
        compareDesc = function(rowA, rowB) {
            return rowB.cells[colNum].innerHTML - rowA.cells[colNum].innerHTML;
        };
        if (dir==='ASC') {
            compare = compareAsc;
        } else {
            compare = compareDesc;
        }
        rowsArray.sort(compare);
        tbody.append(...rowsArray);
};


// click en encabezados para ordenar en forma numerica
// click con Ctrl presionado en encabezados para ordenar en forma alfabetica
document.addEventListener('click', ()=>{
    if(event.target.tagName=== 'TH' && (event.altKey===false||event.ctrlKey===false)) {
        let th = event.target;
        sortGridNumerica(th.cellIndex,'ASC');
    }
    if(event.target.tagName=== 'TH' && (event.altKey===true||event.ctrlKey===true)) {
	let th = event.target;
	sortGridNumerica(th.cellIndex,'DESC');
    }
});


// click para seleccionar/deseleccionar filas de la tabla.
// click con alt presionado deselecciona todo
// hay una class "noselect" que se le puede agregar a la tabla para que no tenga seleccion
document.addEventListener('click', ()=>{
        if(event.target.tagName==='TD') {
	    if (event.target.parentElement.parentElement.parentElement.classList.contains("noselect")) return;
            markSelected();
        };
        if(event.target.tagName=== 'TD' && event.altKey===true){
	    if (event.target.parentElement.parentElement.parentElement.classList.contains("noselect")) return;
            t=event.target.parentElement.parentElement.parentElement;
            restaurar(t);
        };
});


// restauro el table al hacer click en la fila subtotal
document.addEventListener('click', ()=>{
    if(event.target.parentElement.classList.contains('subtotal')){
        t=event.target.parentElement.parentElement.parentElement;
        restaurar(t);
    }
});



document.addEventListener('mousedown',()=>{
    if(event.target.tagName==='TD') event.preventDefault();
    if(event.target.tagName==='TH') event.preventDefault();
    // prevenimos la accion de seleccionar valores
    // de la tabla que es molesto y no sirve para nada.
});


document.addEventListener('mouseover',()=>{
    if(event.target.tagName==='TD' &&  event.ctrlKey===true) {
                    if(!event.target.parentElement.parentElement.parentElement.classList.contains('noselect')){
                    // este if condiciona a que la tabla no tenga la clase noselect
                        markSelected('add');
                    }
                }
});


document.addEventListener('contextmenu', ()=>{
    // sort tabla por columnas con boton derecho en el encabezado
    event.preventDefault();
    // prevenDefault para que no funcione como esta predeterminado
    if(!event.target.parentElement.parentElement.parentElement.classList.contains('nototal')&&
       !event.target.parentElement.parentElement.parentElement.classList.contains('noselect')){
        if(event.target.tagName=== 'TD'){
            t=event.target.parentElement.parentElement.parentElement;
            totalizar(t);
        };
        }
        // el event.target entrega el elemento clickado, si su tagName es TD
        // buscampos el parent del parent del parent que es la tabla
        // y lanzamos la funcion restaurar(tabla)

        // luego si no es un TH terminamos
        if(event.target.tagName!= 'TH') return;
        // si es un TH lanzamos la funcion sortGrid
        if(event.target.tagName=== 'TH' && (event.altKey===false||event.ctrlKey===false)) {
        let th = event.target;
            sortGrid(th.cellIndex,'ASC');
        }
        // con Alt o Ctrl ordenamos en sentido desc
	if(event.target.tagName=== 'TH' && (event.altKey===true||event.ctrlKey===true)) {
	    let th = event.target;
		sortGrid(th.cellIndex,'DESC');
	    }
    });


// Funcion usada en datatables vainilla js para dar formato a los datos obtenidos de json-flask
function dataWrapper(datos){
    let obj = {
    headings: Object.keys(datos[0]),
    data: []
    };
    for ( let i = 0; i < datos.length; i++ ) {
        obj.data[i] = [];
        for (let p in datos[i]) {
            if( datos[i].hasOwnProperty(p) ) {
                obj.data[i].push(datos[i][p]);
            }
        }
    }
    return obj;
}

// wrapper a Swal
function msgSuccess(title, text) {
    Swal.fire({
	title: title,
	text: text,
	icon: 'success',
	timer:3000});
}
function msgError(title, text) {
    Swal.fire({
	title: title,
	text: text,
	icon: 'error',
	timer:3000});
}
function msgDelay(text) {
    Swal.fire({
	title: 'Aguarde...',
	text: text,
	icon: 'warning',
	timer: 20000,
	timerProgressBar: true});
}
// verifica si es desktop o mobile
 /* Storing user's device details in a variable*/
        let details = navigator.userAgent;
        /* Creating a regular expression
        containing some mobile devices keywords
        to search it in details string*/
        let regexp = /android|iphone|kindle|ipad/i;
        /* Using test() method to search regexp in details
        it returns boolean value*/
        let isMobileDevice = regexp.test(details);

// bulma change theme dark-light

const btnMenu = document.getElementById("btnMenu");
const menu = document.getElementById("menu");
btnMenu.addEventListener('click',()=>{
    menu.classList.toggle('mostrar');
});

function toggleTheme() {
            var theme = document.getElementById('bulma');
            // Change the value of href attribute
            // to change the css sheet.
            if (theme.getAttribute('href') == "https://unpkg.com/bulmaswatch/flatly/bulmaswatch.min.css") {
                theme.setAttribute('href', "https://unpkg.com/bulmaswatch/darkly/bulmaswatch.min.css");
                localStorage.setItem("bulma", "https://unpkg.com/bulmaswatch/darkly/bulmaswatch.min.css");
            } else {
                theme.setAttribute('href', "https://unpkg.com/bulmaswatch/flatly/bulmaswatch.min.css");
                localStorage.setItem("bulma", "https://unpkg.com/bulmaswatch/flatly/bulmaswatch.min.css");
            }
        }
document.addEventListener("DOMContentLoaded",(e)=>{
    let bulma = localStorage.getItem('bulma');
    const theme = document.getElementById('bulma');
    theme.setAttribute('href',bulma);
});
