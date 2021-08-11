odoo.define('awb_payment_allocation.AccountPaymentOdoo', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ReconciliationModel = require('account.ReconciliationModel');
var ReconciliationRenderer = require('account.ReconciliationRenderer');

var Widget = require('web.Widget');
var FieldManagerMixin = require('web.FieldManagerMixin');
var relational_fields = require('web.relational_fields');
var basic_fields = require('web.basic_fields');
var core = require('web.core');
var time = require('web.time');
var session = require('web.session');
var qweb = core.qweb;
var _t = core._t;

	var AccountPayment = require('account.ReconciliationRenderer');
	console.log("TEST 2222", AccountPayment)
		var self = this;

	var PaymentAlloc = require('account.ReconciliationClientAction');
	console.log("TEST 1111", PaymentAlloc)
	// this.onload = function(){myScript};
		
	AccountPayment.LineRenderer.include({
		// /**
		//  * @override
		//  * @param {jQueryElement} $el
		//  */
		// start: function () {
		// 	var self = this;
		// 	var def1 = this._makePartnerRecord(this._initialState.st_line.partner_id, this._initialState.st_line.partner_name).then(function (recordID) {
		// 		self.fields = {
		// 			partner_id : new relational_fields.FieldMany2One(self,
		// 				'partner_id',
		// 				self.model.get(recordID), {
		// 					mode: 'edit',
		// 					attrs: {
		// 						placeholder: self._initialState.st_line.communication_partner_name || _t('Select Partner'),
		// 					}
		// 				}
		// 			)
		// 		};
		// 		self.fields.partner_id.insertAfter(self.$('.accounting_view caption .o_buttons'));
		// 	});
		// 	$('<span class="line_info_button fa fa-info-circle"/>')
		// 		.appendTo(this.$('thead .cell_info_popover'))
		// 		.attr("data-content", qweb.render('reconciliation.line.statement_line.details', {'state': this._initialState}));
		// 	this.$el.popover({
		// 		'selector': '.line_info_button',
		// 		'placement': 'left',
		// 		'container': this.$el,
		// 		'html': true,
		// 		// disable bootstrap sanitizer because we use a table that has been
		// 		// rendered using qweb.render so it is safe and also because sanitizer escape table by default.
		// 		'sanitize': false,
		// 		'trigger': 'hover',
		// 		'animation': false,
		// 		'toggle': 'popover'
		// 	});

		// 	// var moveLineId = $el.closest('.mv_line').data('line-id');
		// 	// self._onSelectMoveLine()
		// 	// console.log("TEST 4444", moveLineId)
		// 	alert("EXAMPLE ALERT ");

		// 	var def2 = this._super.apply(this, arguments);
		// 	console.log("TEST 3333", def2)
		// 	return Promise.all([def1, def2]);
		// },

		/**
		 * @private
		 * @param {MouseEvent} event
		 */
		_onSelectMoveLine: function (event) {
			var $el = $(event.target);
			$el.prop('disabled', true);
			this._destroyPopover($el);
			var moveLineId = $el.closest('.mv_line').data('line-id');
			console.log("TEST 4444", moveLineId);
			this.trigger_up('add_proposition', {'data': moveLineId});
		},

		/**
	 * update the statement line rendering
	 *
	 * @param {object} state - statement line
	 */
	update: function (state) {
		var self = this;
		// isValid
		var to_check_checked = !!(state.to_check);
		this.$('caption .o_buttons button.o_validate').toggleClass('d-none', !!state.balance.type && !to_check_checked);
		this.$('caption .o_buttons button.o_reconcile').toggleClass('d-none', state.balance.type <= 0 || to_check_checked);
		this.$('caption .o_buttons .o_no_valid').toggleClass('d-none', state.balance.type >= 0);
		self.$('caption .o_buttons button.o_validate').toggleClass('text-warning', to_check_checked);

		// partner_id
		this._makePartnerRecord(state.st_line.partner_id, state.st_line.partner_name).then(function (recordID) {
			self.fields.partner_id.reset(self.model.get(recordID));
			self.$el.attr('data-partner', state.st_line.partner_id);
		});

		// mode
		this.$el.data('mode', state.mode).attr('data-mode', state.mode);
		this.$('.o_notebook li a').attr('aria-selected', false);
		this.$('.o_notebook li a').removeClass('active');
		this.$('.o_notebook .tab-content .tab-pane').removeClass('active');
		this.$('.o_notebook li a[href*="notebook_page_' + state.mode + '"]').attr('aria-selected', true);
		this.$('.o_notebook li a[href*="notebook_page_' + state.mode + '"]').addClass('active');
		this.$('.o_notebook .tab-content .tab-pane[id*="notebook_page_' + state.mode + '"]').addClass('active');
		this.$('.create, .match').each(function () {
			$(this).removeAttr('style');
		});

		// reconciliation_proposition
		var $props = this.$('.accounting_view tbody').empty();

		// Search propositions that could be a partial credit/debit.
		var props = [];
		var balance = state.balance.amount_currency;
		_.each(state.reconciliation_proposition, function (prop) {
			if (prop.display) {
				props.push(prop);
			}
		});

		_.each(props, function (line) {
			var $line = $(qweb.render("reconciliation.line.mv_line", {'line': line, 'state': state, 'proposition': true}));
			if (!isNaN(line.id)) {
				$('<span class="line_info_button fa fa-info-circle"/>')
					.appendTo($line.find('.cell_info_popover'))
					.attr("data-content", qweb.render('reconciliation.line.mv_line.details', {'line': line}));
			}
			$props.append($line);
		});

		// mv_lines
		var matching_modes = self.model.modes.filter(x => x.startsWith('match'));
		for (let i = 0; i < matching_modes.length; i++) {
			var stateMvLines = state['mv_lines_'+matching_modes[i]] || [];
			var recs_count = stateMvLines.length > 0 ? stateMvLines[0].recs_count : 0;
			var remaining = recs_count - stateMvLines.length;
			var $mv_lines = this.$('div[id*="notebook_page_' + matching_modes[i] + '"] .match table tbody').empty();
			this.$('.o_notebook li a[href*="notebook_page_' + matching_modes[i] + '"]').parent().toggleClass('d-none', stateMvLines.length === 0 && !state['filter_'+matching_modes[i]]);

			// console.log("TEST 5555", stateMvLines[i].name)
			// var this_mv_line = stateMvLines[i].name
			if (stateMvLines.length != 0) {
				var mv_line_id = stateMvLines[i].id
				console.log("TEST 5555", stateMvLines[i].name)
				console.log("TEST 6666", stateMvLines.length)
				console.log("TEST 7777", matching_modes.length)
				this.trigger_up('add_proposition', {'data': mv_line_id});
			}

			_.each(stateMvLines, function (line) {
				var $line = $(qweb.render("reconciliation.line.mv_line", {'line': line, 'state': state}));
				if (!isNaN(line.id)) {
					$('<span class="line_info_button fa fa-info-circle"/>')
					.appendTo($line.find('.cell_info_popover'))
					.attr("data-content", qweb.render('reconciliation.line.mv_line.details', {'line': line}));
				}
				$mv_lines.append($line);
			});

			this.$('div[id*="notebook_page_' + matching_modes[i] + '"] .match div.load-more').toggle(remaining > 0);
			this.$('div[id*="notebook_page_' + matching_modes[i] + '"] .match div.load-more span').text(remaining);
		}


		// balance
		this.$('.popover').remove();
		this.$('table tfoot').html(qweb.render("reconciliation.line.balance", {'state': state}));

		// create form
		if (state.createForm) {
			var createPromise;
			if (!this.fields.account_id) {
				createPromise = this._renderCreate(state);
			}
			Promise.resolve(createPromise).then(function(){
				var data = self.model.get(self.handleCreateRecord).data;
				return self.model.notifyChanges(self.handleCreateRecord, state.createForm)
					.then(function () {
					// FIXME can't it directly written REPLACE_WITH ids=state.createForm.analytic_tag_ids
						return self.model.notifyChanges(self.handleCreateRecord, {analytic_tag_ids: {operation: 'REPLACE_WITH', ids: []}})
					})
					.then(function (){
						var defs = [];
						_.each(state.createForm.analytic_tag_ids, function (tag) {
							defs.push(self.model.notifyChanges(self.handleCreateRecord, {analytic_tag_ids: {operation: 'ADD_M2M', ids: tag}}));
						});
						return Promise.all(defs);
					})
					.then(function () {
						return self.model.notifyChanges(self.handleCreateRecord, {tax_ids: {operation: 'REPLACE_WITH', ids: []}})
					})
					.then(function (){
						var defs = [];
						_.each(state.createForm.tax_ids, function (tag) {
							defs.push(self.model.notifyChanges(self.handleCreateRecord, {tax_ids: {operation: 'ADD_M2M', ids: tag}}));
						});
						return Promise.all(defs);
					})
					.then(function () {
						var record = self.model.get(self.handleCreateRecord);
						_.each(self.fields, function (field, fieldName) {
							if (self._avoidFieldUpdate[fieldName]) return;
							if (fieldName === "partner_id") return;
							if ((data[fieldName] || state.createForm[fieldName]) && !_.isEqual(state.createForm[fieldName], data[fieldName])) {
								field.reset(record);
							}
							if (fieldName === 'tax_ids') {
								if (!state.createForm[fieldName].length || state.createForm[fieldName].length > 1) {
									$('.create_force_tax_included').addClass('d-none');
								}
								else {
									$('.create_force_tax_included').removeClass('d-none');
									var price_include = state.createForm[fieldName][0].price_include;
									var force_tax_included = state.createForm[fieldName][0].force_tax_included;
									self.$('.create_force_tax_included input').prop('checked', force_tax_included);
									self.$('.create_force_tax_included input').prop('disabled', price_include);
								}
							}
						});
						if (state.to_check) {
							// Set the to_check field to true if global to_check is set
							self.$('.create_to_check input').prop('checked', state.to_check).change();
						}
						return true;
					});
			});
		}
		this.$('.create .add_line').toggle(!!state.balance.amount_currency);
		},

	})
		

})
	


