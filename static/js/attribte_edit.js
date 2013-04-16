attr_id = {{ id }}
        attr_version = {{ version }}

        $.ajaxSetup({ 
             beforeSend: function(xhr, settings) {
                 function getCookie(name) {
                     var cookieValue = null;
                     if (document.cookie && document.cookie != '') {
                         var cookies = document.cookie.split(';');
                         for (var i = 0; i < cookies.length; i++) {
                             var cookie = jQuery.trim(cookies[i]);
                             // Does this cookie string begin with the name we want?
                         if (cookie.substring(0, name.length + 1) == (name + '=')) {
                             cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                             break;
                         }
                     }
                 }
                 return cookieValue;
                 }
                 if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                     // Only send the token to relative URLs i.e. locally.
                     xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                 }
             } 
        });
    
        $('.js-nominal-item').change(function(){
            var old_value = $(this).data('oldValue')
            var new_value = $(this).val()
            var obj = $(this)
            if (old_value && new_value && old_value != new_value) {
                $.ajax({
                    type: 'POST',
                    url: "{% url 'ajax_change_attribute' %}",
                    dataType: "json",
                    data: {
                        'id': attr_id,
                        'version': attr_version,
                        'operation': 'rename',
                        'data': JSON.stringify({"value": old_value, "new_value": new_value})
                        },
                    success: function (data){
                        attr_id = data.id
                        attr_version = data.version
                        obj.data('oldValue', new_value)
                        alert ( " Done ! " + data );
                    },
                    error: function(xhr,err){
                        alert("readyState: "+xhr.readyState+"\nstatus: "+xhr.status);
                        obj.val(old_value)
                        alert("responseText: "+xhr.responseText);

                    },
                });

                // $.post("{% url 'ajax_change_attribute' %}", {
                //     'id': {{ id }},
                //     'version': {{ version }},
                //     'operation': 'rename',
                //     'data': JSON.stringify({"value": old_value, "new_value": new_value})
                //     }
                // )
                // .done(function(data){
                //     attr_id = data.id
                //     attr_version = data.version
                //     alert('success!')
                // })
                // .fail(alert('fail!!!'))
            }
        })

        function add_nominal_option() {
            // var old_value = $(this).data('oldValue')
            obj = $('#add-nominal-item')
            var new_value = obj.val()
            if (new_value) {
                $.ajax({
                    type: 'POST',
                    url: "{% url 'ajax_change_attribute' %}",
                    dataType: "json",
                    data: {
                        'id': attr_id,
                        'version': attr_version,
                        'operation': 'add',
                        'data': JSON.stringify({"value": new_value})
                    },
                    success: function (data){
                        attr_id = data.id
                        attr_version = data.version
                        obj.data('oldValue', new_value)
                        // obj.addClass('js-nominal-item').removeClass('js-nominal-item-new')
                        alert ( " Done ! " + data );
                    },
                    error: function(xhr,err){
                        alert("readyState: "+xhr.readyState+"\nstatus: "+xhr.status);
                        alert("responseText: "+xhr.responseText);
                    },
                });
            }
        }

        
        $type_descr = $('#id_atype option:selected').val()
        $('.js-description-form').hide();
        $('#form-for-' + $type_descr).show();

        $('#id_atype').change(function(){
            $type_descr = $('#id_atype option:selected').val()
            $('.js-description-form').hide();
            $('#form-for-' + $type_descr).show();
        })
        // $('#table-nominal-id tr.item').hover(
        //     function(){
        //         $(this).find('td:last a').show();
        //     },
        //     function(){
        //         $(this).find('td:last a').hide();
        //     }
        // )
        
        // $('#add-nominal-item').forcus()
        // $('#form-for-nominal .js-check_default').click(function(){
        //     if ($(this).is(':checked')) {
        //         $('#form-for-nominal .js-check_default').prop('checked', false);
        //         $(this).prop('checked', true)
        //     };
        // })


        // Add Nominal item
        $('#submit-add-nominal-item').click(function(){
            $add_nominal = $('#add-nominal-item')
            if ($add_nominal.val()) {

                obj = $('#add-nominal-item')
                var new_value = obj.val()
                if (new_value) {
                    $.ajax({
                        type: 'POST',
                        url: "{% url 'ajax_change_attribute' %}",
                        dataType: "json",
                        data: {
                            'id': attr_id,
                            'version': attr_version,
                            'operation': 'add',
                            'data': JSON.stringify({"value": new_value})
                        },
                        success: function (data){
                            attr_id = data.id
                            attr_version = data.version
                            obj.data('oldValue', new_value)
                            // obj.addClass('js-nominal-item').removeClass('js-nominal-item-new')
                            alert ( " Done ! " + data );
                        },
                        error: function(xhr,err){
                            alert("readyState: "+xhr.readyState+"\nstatus: "+xhr.status);
                            alert("responseText: "+xhr.responseText);
                        },
                    });
                }


                $('#table-nominal-id tr.js_add_item').before(
                    '<tr class="item"> \
                        <td><input name="descr_nominal" class="js-nominal-item-new" \
                            data-old-value="" value="' + $add_nominal.val() + '"> \
                        </td> \
                        <td><input type="radio" class="js-nominal-default" name="descr_nominal_default" value="' + $add_nominal.val() + '"></td> \
                        <td><a class="js-nominal-delete btn btn-mini btn-danger">x</a></td> \
                    </tr>'
                    )
                $add_nominal.val('');
                if ($('.js-nominal-default:checked').attr('checked')) {}
                else {
                    $('.js-nominal-default:first').prop('checked', true)
                };
                
            };

        });

        max_width = 

        // Add Scale item
        $('#submit-add-scale-item').click(function(){
            $add_scale = $('#add-scale-item')
            if ($add_scale.val()) {
                    $('#table-scale-id tbody').append(
                        '<tr class="item"> \
                            <td><input name="descr_scale" value="' + $add_scale.val() + '"></td> \
                            <td class="js-scale-name"><input name="descr_scale" value="' + $add_scale.val() + '"></td> \
                            <td><input type="radio" name="descr_scale_default" value="' + $add_scale.val() + '"></td> \
                            <td><a class="js-scale-delete btn btn-mini btn-danger">x</a></td> \
                        </tr>'
                        );
                $add_scale.val('');
                // $('#sortable .item').each(function(){
                //     $(this).find('td:first').html($(this).index());
                // });
            };
        });

        // Delete Nominal Button
        $('#form-for-nominal').delegate('.js-nominal-delete', 'click', function(){
            // TODO if delete checked item check other item as default
            $(this).parent().parent().remove()

            if ($('.js-nominal-default:checked').attr('checked')) {}
            else {
                $('.js-nominal-default:first').prop('checked', true)
            };
        })

        // Delete Scale Button
        $('#form-for-scale').delegate('.js-scale-delete', 'click', function(){
            // TODO if delete checked item check other item as default
            $(this).parent().parent().remove()
            // $('#sortable .item').each(function(){
            //     $(this).find('td:first').html($(this).index());
            // });
        })


        // attr_data = {{ attr_data|jsonify }}

        // After Submit Form
        // $('#attribute-form-id').submit(function(){
            // $('#attr_data_id').val(JSON.stringify(files_dict));
        //     // nominal_list = []
        //     // $(".js-nominal-name").each(function(i, item) {
        //     //     // nominal_names = $.map($(item), function(option, i) {
        //     //     //     return $(option).html();
        //     //     // }).join(", ");
        //     //     nominal_list = nominal_list.concat($(item).html())
        //     // // }).join(", ")
        //     //     // alert(nominal_array);
        //     // });
        //     // $('#descr_nominal').val(nominal_list.join(", "));

        //     scale_value = ""
        //     $('.js-scale-name').each(function(i, item) {
        //         if (i==0) {
        //             scale_value = $(item).html() + ", " + $(item).prev().html()
        //         }
        //         else {
        //             scale_value = scale_value + "; " + $(item).html() + ", " + $(item).prev().html()
        //         }
        //         // scale_dict[$(item).html()] = $(item).after().html()
        //         // scale_value = scale_value + "; " + $(item).html() + ", " + $(item).next().html()
        //     });
        //     $('#descr_scale').val(scale_value);
        //     // return false;
        // });