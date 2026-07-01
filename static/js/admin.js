(function(){

'use strict';

/* ============================================================
ACTIVE SIDEBAR
============================================================ */

function highlightActiveLink(){

```
const currentPath =
    window.location.pathname;

const links =
    document.querySelectorAll(
        '.nav-sidebar .nav-link'
    );

links.forEach(link => {

    const href =
        link.getAttribute('href');

    if(!href){
        return;
    }

    if(
        currentPath === href ||
        (
            href !== '/' &&
            currentPath.startsWith(href)
        )
    ){

        link.classList.add('active');

        setTimeout(() => {

            link.scrollIntoView({
                block:'center',
                behavior:'smooth'
            });

        },200);
    }
});
```

}

/* ============================================================
LOADER
============================================================ */

function hideLoader(){

```
const loader =
    document.getElementById(
        'page-loader'
    );

if(!loader){
    return;
}

loader.style.transition =
    'opacity .4s ease';

loader.style.opacity = '0';

setTimeout(() => {

    loader.remove();

},400);
```

}

/* ============================================================
PAGE NAVIGATION
============================================================ */

function setupNavigationLoader(){

```
document
.querySelectorAll('a')
.forEach(link => {

    link.addEventListener(
        'click',
        function(){

            if(
                this.href &&
                !this.href.startsWith('javascript:')
            ){

                const loader =
                    document.getElementById(
                        'page-loader'
                    );

                if(loader){

                    loader.style.display =
                        'flex';

                    loader.style.opacity =
                        '1';
                }
            }
        }
    );
});
```

}

/* ============================================================
AUTO HIDE MESSAGES
============================================================ */

function autoHideMessages(){

```
const alerts =
    document.querySelectorAll(
        '.alert, .messagelist li'
    );

alerts.forEach(alert => {

    setTimeout(() => {

        alert.style.transition =
            'opacity .5s ease';

        alert.style.opacity = '0';

        setTimeout(() => {

            if(alert.parentNode){
                alert.remove();
            }

        },500);

    },5000);
});
```

}

/* ============================================================
INIT
============================================================ */

document.addEventListener(
'DOMContentLoaded',
function(){

```
    highlightActiveLink();
    setupNavigationLoader();
    autoHideMessages();
}
```

);

window.addEventListener(
'load',
hideLoader
);

})();
