
(function($){
    // var Document = Backbone.Model.extend({
    // });
    
    // var AppState = {
    // username: ""
    // }

    var AppState = Backbone.Model.extend({
        localStorage: new Backbone.LocalStorage('todos-backbone'),
        defaults: {
            username: "",
            password: "",
            sessionkey: "",
            // state: "start"
        }
    });

    var ObjectItem = Backbone.Model.extend({
        localStorage: new Backbone.LocalStorage('todos-backbone'),
        
        defaults: {
            name: "",
            creator: "",
            // state: "start"
        }
    });

    var appState = new AppState();

    var UserNameModel = Backbone.Model.extend({ // Модель пользователя
        defaults: {
            "Name": ""
        }
    });

    var Family = Backbone.Collection.extend({ // Коллекция пользователей
        model: UserNameModel,

        checkUser: function (username) { // Проверка пользователя
            var findResult = this.find(function (user) { return user.get("Name") == username })
            return findResult != null;
        }
    });

    var MyFamily = new Family([ // Моя семья
                { Name: "Саша" },
                { Name: "Юля" },
                { Name: "Елизар" },
                { Name: "test" }
            ]);

    // var Family = ["Саша", "Юля", "Елизар", "test"]; // Моя семья

    // var Controller = Backbone.Router.extend({
    //     routes: {
    //         "": "start", // Пустой hash-тэг
    //         "!/": "start", // Начальная страница
    //         "!/success": "success", // Блок удачи
    //         "!/error": "error" // Блок ошибки
    //     },

    //     start: function () {
    //         $(".block").hide(); // Прячем все блоки
    //         $("#start").show(); // Показываем нужный
    //     },

    //     success: function () {
    //         alert();
    //         $(".block").hide();
    //         $("#success").show();
    //     },

    //     error: function () {
    //         $(".block").hide();
    //         $("#error").show();
    //     }
    // });
    
    var Block = Backbone.View.extend({

        el: $("#block"), // DOM элемент widget'а

        events: {
            "click input:button": "check" // Обработчик клика на кнопке "Проверить"
        },

        templates: { // Шаблоны на разное состояние
            "start": _.template($('#start').html()),
            "success": _.template($('#success').html()),
            "error": _.template($('#error').html())
        },

        initialize: function () { // Подписка на событие модели
            this.model.bind('change', this.render, this);
        },

        render: function () {
            var state = this.model.get("state");
            $(this.el).html(this.templates[state](this.model.toJSON()));
            return this;
        },

        check: function () {
            var username = $(this.el).find("input:text").val();
            // var find = (_.detect(Family, function (elem) { return elem == username })); // Проверка имени пользователя
            var find = MyFamily.checkUser(username); // Проверка имени пользователя
            appState.set({ // Сохранение имени пользователя и состояния
                "state": find ? "success" : "error",
                "username": username
            }); 
        },
    });


    var block = new Block({ model: appState });
    appState.trigger("change");


    // var Start = Backbone.View.extend({
    //     el: $("#block"), // DOM элемент widget'а

    //     template: _.template($('#start').html()),

    //     events: {
    //         "click input:button": "check" // Обработчик клика на кнопке "Проверить"
    //     },

    //     check: function () {
    //         AppState.username = $(this.el).find("input:text").val(); // Сохранение имени пользователя
    //         if (_.detect(Family, function (elem) { return elem == AppState.username })) // Проверка имени пользователя
    //         if (AppState.username == "test") // Проверка имени пользователя
    //             controller.navigate("!/success", true); // переход на страницу success
    //         else
    //             controller.navigate("!/error", true); // переход на страницу error
    //     },

    //     render: function () {
    //         $(this.el).html(this.template());
    //     }
    // });

    // var Success = Backbone.View.extend({
    //     el: $("#block"), // DOM элемент widget'а

    //     template: _.template($('#success').html()),

    //     render: function () {
    //         $(this.el).html(this.template(AppState));
    //     }
    // });

    // var Error = Backbone.View.extend({
    //     el: $("#block"), // DOM элемент widget'а

    //     template: _.template($('#error').html()),

    //     render: function () {
    //         $(this.el).html(this.template(AppState));
    //     }
    // });

    // Views = { 
    //             start: new Start(),
    //             success: new Success(),
    //             error: new Error()
    //         };

    // var start = new Start();

    // var Controller = Backbone.Router.extend({
    //     routes: {
    //         "": "start", // Пустой hash-тэг
    //         "!/": "start", // Начальная страница
    //         "!/success": "success", // Блок удачи
    //         "!/error": "error" // Блок ошибки
    //     },

    //     start: function () {
    //         if (Views.start != null) {
    //             Views.start.render();
    //         }
    //     },

    //     success: function () {
    //         if (Views.success != null) {
    //             Views.success.render();
    //         }
    //     },

    //     error: function () {
    //         if (Views.error != null) {
    //             Views.error.render();
    //         }
    //     }
    // });

    var Controller = Backbone.Router.extend({
        routes: {
            "": "start", // Пустой hash-тэг
            "!/": "start", // Начальная страница
            "!/success": "success", // Блок удачи
            "!/error": "error" // Блок ошибки
        },

        start: function () {
            appState.set({ state: "start" });
        },

        success: function () {
            appState.set({ state: "success" });
        },

        error: function () {
            appState.set({ state: "error" });
        }
    });

    var controller = new Controller(); // Создаём контроллер

    appState.bind("change:state", function () { // подписка на смену состояния для контроллера
        var state = this.get("state");
        if (state == "start")
            controller.navigate("!/", false); // false потому, что нам не надо 
                                              // вызывать обработчик у Router
        else
            controller.navigate("!/" + state, false);
    });

    Backbone.history.start();  // Запускаем HTML5 History push  


})(jQuery);
