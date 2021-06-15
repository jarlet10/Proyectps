function modoUso() {
    echo "-----------------------------------------------"
    echo "|                Modo Uso                     |"
    echo "|                                             |"
    echo "|        Arranca el proyecto Django           |"
    echo "|                                             |"
    echo "|           ./run.sh archivo.env              |"
    echo "-----------------------------------------------"
}

function validar(){
    [[ "$1" ]] || { echo "Necesitas Selecionar un archivo.env"; modoUso; exit 1; }
    [[ -f "$1" ]] || { echo "El parametro 1 debe ser un archivo valido"; modoUso; exit 1; }
}

validar "$@"

for linea in $(cat "$1"); do
    export $linea
done

python manage.py runserver