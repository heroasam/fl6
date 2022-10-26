let listaheads = document.querySelectorAll('thead');
$theads = Array.from(listaheads);
$theads.forEach($thead=>{
    let heads = $thead.children.length;
    if(heads===3) {
	$thead.removeChild($thead.lastElementChild);
	$thead.removeChild($thead.firstElementChild);
	heads = $thead.children.length;
    }
})

function nop(pesos){
    let signo = pesos.substr(0,1);
  if (signo=="$"){
      let len =  pesos.length - 1;
      let valor = pesos.substr(1,len);
      return valor;
  }else{
      return pesos;
  }
}

const totalizar = (tableId)=>{
    let table;
    if(typeof tableId =='string'){
        table = document.getElementById(tableId);
    }else{
        table = tableId;
    }
        let tbody = table.querySelector('tbody');
        let rowsArray = Array.from(tbody.rows);
        let rowIndex=[];
        rowsArray.forEach((row)=>{
            if(row.classList.contains('is-selected')) {
                rowIndex.push(row.rowIndex-1);
                //hago factor 1 pq se eliminan las filas sobrantes y se deja 1
            }
            if(row.classList.contains('subtotal')){
                row.remove();
            };
        });
        let maxRow = Math.max(...rowIndex)+1;
        let $rowTotal = tbody.insertRow(maxRow);
        $rowTotal.classList.add('subtotal');

    const cols = rowsArray[0].children.length; // determino la cant columnas
    for (let i=0;i<cols;i++){
        $rowTotal.insertCell(i);
    }
    $rowTotal.cells[0].innerHTML = "Subtotal";

    const $ths = table.querySelectorAll('th');
    const $thtotal = [];
    const $thclass = [];
    Array.from($ths).forEach(th=>
        {if(th.classList.contains('sumar')){
            $thtotal.push(th.cellIndex);
            $thclass.push(Array.from(rowsArray[0].cells[th.cellIndex].classList));
        }});
    //para el caso de pandas donde no se puede usar el sistema de classList
    if($thtotal.length==0) {
        for(let n=1;n<cols;n++) {
            $thtotal.push(n);
        }
    }
        for(let index in $thtotal){
            let i = parseInt($thtotal[index]);
        let col = [];
        rowIndex.forEach((ix)=>{
            col.push(nop(tbody.rows[ix].cells[i].innerText));
        });
        let total = col.reduce((a,b)=>Number(a)+Number(b),0);
        let $cell = $rowTotal.cells[i];
            if (!(Number.isNaN(total))) $cell.innerHTML = total;
            if($thclass.length) $cell.classList.add(...$thclass[index]);
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
        let $rowSubTotal = tableId.querySelectorAll('.subtotal');
        $rowSubTotal.forEach((row)=>{
            row.remove();
        });
    };


// markSelected es un toggle que selecciona/deselecciona
const markSelected = (forma=null)=>{
    if (event.target.parentElement?.parentElement?.tagName!='TBODY') return;
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


const markAll = (tableId)=>{
    let table;
    if(typeof tableId =='string'){
        table = document.getElementById(tableId);
    }else{
        table = tableId;
    }
    const $tbody = table.querySelector('tbody');
    Array.from($tbody.rows).forEach(row=>{
        row.classList.add('is-selected');
    });
};


const sortGrid = (colNum,dir,table)=>{
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


const sortGridNumerica = (colNum,dir,table)=>{
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

let i_num_asc = '<i class="fa fa-sort-numeric-asc" aria-hidden="true"></i>';
let i_alpha_asc = '<i class="fa fa-sort-alpha-asc" aria-hidden="true"></i>';
let i_num_desc = '<i class="fa fa-sort-numeric-desc" aria-hidden="true"></i>';
let i_alpha_desc = '<i class="fa fa-sort-alpha-desc" aria-hidden="true"></i>';
let colOrder={};
document.addEventListener('click', ()=>{
    if(event.target.tagName=== 'TH') {
        let t=event.target.parentElement.parentElement?.parentElement || 0;
        let th = event.target;
        let col = th.cellIndex;
        let numeric = th.classList.contains('numeric');
        if(numeric){
            if(colOrder.col=='ASC'){
            sortGridNumerica(th.cellIndex,'DESC',t);
                agregarIcon(th,i_num_desc);
                colOrder.col='DESC';
            }else{
            sortGridNumerica(th.cellIndex,'ASC',t);
                agregarIcon(th,i_num_asc);
                colOrder.col='ASC';
            }
        }else{
            if(colOrder.col=='ASC'){
            sortGrid(th.cellIndex,'DESC',t);
                agregarIcon(th,i_alpha_desc);
                colOrder.col='DESC';
            }else{
            sortGrid(th.cellIndex,'ASC',t);
                agregarIcon(th,i_alpha_asc);
                colOrder.col='ASC';
            }
        }
    }
});
const agregarIcon=(th,icon)=>{
    for(let item of th.parentElement.children){
        item.innerHTML=item.innerText;
    }
    if(th.clientWidth<100) th.width=100;
    th.innerHTML=th.innerText.trim()+' '+icon;
};

// click para seleccionar/deseleccionar filas de la tabla.
// click con alt presionado deselecciona todo
// hay una class "noselect" que se le puede agregar a la tabla para que no tenga seleccion
document.addEventListener('click', ()=>{
        if(event.target.tagName==='TD') {
        let t=event.target.parentElement?.parentElement?.parentElement || 0;
	    if (event.target.parentElement?.parentElement?.parentElement?.classList?.contains("noselect")) return;
            markSelected();

        if(event.target.parentElement?.classList.contains('subtotal')){
            restaurar(t);
        };

        };
        if(event.target.tagName=== 'TD' && event.altKey===true){
        let t=event.target.parentElement.parentElement.parentElement || 0;
	    if (event.target.parentElement.parentElement.parentElement.classList.contains("noselect")) return;
            restaurar(t);
        };
});

// restauro el table al hacer click en la fila subtotal
// document.addEventListener('click', ()=>{
//     if(event.target.tagName==='TD'){
//     let t=event.target.parentElement?.parentElement?.parentElement || 0;
//     if(event.target.parentElement.classList.contains('subtotal')){
//         restaurar(t);
//     }
//     }
// });


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
                        // fixme:cuando este evento se dispara el wheel achica la letra.
                        event.target.removeEventListener('onwheel',
                                                         markSelected('add'));
                    }
                }
});

const getTableId = (element)=>{
    let table;
    switch (element.tagName){
        case 'TD' :
            table = element.parentElement.parentElement.parentElement
            return table;
            break;
        case 'TH' :
            table = element.parentElement.parentElement.parentElement
            return table;
            break;
        case 'TR' :
            table = element.parentElement.parentElement
            return table;
            break;
    }
}



document.addEventListener('contextmenu', ()=>{
    // sort tabla por columnas con boton derecho en el encabezado
    event.preventDefault();
    // prevenDefault para que no funcione como esta predeterminado
    if(!event.target.parentElement.parentElement.parentElement.classList.contains('nototal')&&
       !event.target.parentElement.parentElement.parentElement.classList.contains('noselect')){
        if(event.target.tagName === 'TD'){
        let t=event.target.parentElement.parentElement.parentElement || 0;
            totalizar(t);
        }else if(event.target.tagName === 'TH'){
            let t=getTableId(event.target);
            markAll(t);
            totalizar(t);
        }
    }
});

const limpiarTabla = (tableId)=>{
   let $table = document.getElementById(tableId);
    let $tbody = $table.querySelector('tbody');
    let $thead = $table.querySelector('thead');
    let rowsArray = Array.from($tbody.rows);
    rowsArray.forEach(row=>{
        if(row.classList.contains('subtotal')){
            row.remove();
        }});
    let $tr = $thead.children[0];
    let thsArray = Array.from($tr.children);
    thsArray.forEach(th=>{
        th.innerHTML = th.innerText;
    });
};




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
function msgSuccess(title, text, timer=3000) {
    Swal.fire({
	title: title,
	text: text,
	icon: 'success',
	timer:timer});
}
function msgError(title, text, timer=3000) {
    Swal.fire({
	title: title,
	text: text,
	icon: 'error',
	timer:timer});
}
function msgWarning(title, text, timer=3000) {
    Swal.fire({
	title: title,
	text: text,
	icon: 'warning',
	timer:timer});
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
document.addEventListener("DOMContentLoaded",()=>{
    let bulma = localStorage.getItem('bulma');
    const theme = document.getElementById('bulma');
    theme.setAttribute('href',bulma);
});

function toggleModal(id){
    let $id = document.getElementById(id);
    $id.classList.toggle('is-active'); //
}

function dia(day){
                //formamos el nombre de la clase con la palabra color mas
                //el ultimo digito de los dias para tener solo diez colores
    return "color" + dayjs.utc(day).format('DD').slice(1,2);

}
function autoComplete(url,inputId, suggestionId){
             axios.get(url)
                  .then(res=>{
                      const result = res.data.result;
                      const $input = document.getElementById(inputId);
                      const $suggestions = document.getElementById(suggestionId);
                      $input.addEventListener('keyup',(e)=>{
			              const input = $input.value;
			  $suggestions.innerHTML='';
			  const suggestions = result.filter(item=>{
                  return item.toLocaleLowerCase().includes(input.toLocaleLowerCase());
			  });
			  suggestions.forEach(suggested=>{
                              const $div = document.createElement('div');
                              $div.innerHTML = suggested;
                              $suggestions.appendChild($div);
			  });
			              if(input==='') $suggestions.innerHTML='';
			  if(e.key==='Enter'){
                  $input.value = $suggestions.firstChild.innerHTML;
                  $input.dispatchEvent(new InputEvent('input'));
                  $suggestions.innerHTML='';
			  }
                      });
                      $suggestions.addEventListener('click',(e)=>{
                          $input.value=e.target.innerHTML;
                          $input.dispatchEvent(new InputEvent('input'));
                          $suggestions.innerHTML='';
                      });
                  });
         }
