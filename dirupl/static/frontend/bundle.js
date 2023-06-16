
(function(l, r) { if (!l || l.getElementById('livereloadscript')) return; r = l.createElement('script'); r.async = 1; r.src = '//' + (self.location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1'; r.id = 'livereloadscript'; l.getElementsByTagName('head')[0].appendChild(r) })(self.document);
var app = (function () {
    'use strict';

    function noop() { }
    function add_location(element, file, line, column, char) {
        element.__svelte_meta = {
            loc: { file, line, column, char }
        };
    }
    function run(fn) {
        return fn();
    }
    function blank_object() {
        return Object.create(null);
    }
    function run_all(fns) {
        fns.forEach(run);
    }
    function is_function(thing) {
        return typeof thing === 'function';
    }
    function safe_not_equal(a, b) {
        return a != a ? b == b : a !== b || ((a && typeof a === 'object') || typeof a === 'function');
    }
    function is_empty(obj) {
        return Object.keys(obj).length === 0;
    }

    new Set();
    function append(target, node) {
        target.appendChild(node);
    }
    function insert(target, node, anchor) {
        target.insertBefore(node, anchor || null);
    }
    function detach(node) {
        if (node.parentNode) {
            node.parentNode.removeChild(node);
        }
    }
    function destroy_each(iterations, detaching) {
        for (let i = 0; i < iterations.length; i += 1) {
            if (iterations[i])
                iterations[i].d(detaching);
        }
    }
    function element(name) {
        return document.createElement(name);
    }
    function text(data) {
        return document.createTextNode(data);
    }
    function space() {
        return text(' ');
    }
    function listen(node, event, handler, options) {
        node.addEventListener(event, handler, options);
        return () => node.removeEventListener(event, handler, options);
    }
    function attr(node, attribute, value) {
        if (value == null)
            node.removeAttribute(attribute);
        else if (node.getAttribute(attribute) !== value)
            node.setAttribute(attribute, value);
    }
    function children(element) {
        return Array.from(element.childNodes);
    }
    function custom_event(type, detail, { bubbles = false, cancelable = false } = {}) {
        const e = document.createEvent('CustomEvent');
        e.initCustomEvent(type, bubbles, cancelable, detail);
        return e;
    }

    // we need to store the information for multiple documents because a Svelte application could also contain iframes
    // https://github.com/sveltejs/svelte/issues/3624
    new Map();

    let current_component;
    function set_current_component(component) {
        current_component = component;
    }
    function get_current_component() {
        if (!current_component)
            throw new Error('Function called outside component initialization');
        return current_component;
    }
    /**
     * The `onMount` function schedules a callback to run as soon as the component has been mounted to the DOM.
     * It must be called during the component's initialisation (but doesn't need to live *inside* the component;
     * it can be called from an external module).
     *
     * `onMount` does not run inside a [server-side component](/docs#run-time-server-side-component-api).
     *
     * https://svelte.dev/docs#run-time-svelte-onmount
     */
    function onMount(fn) {
        get_current_component().$$.on_mount.push(fn);
    }

    const dirty_components = [];
    const binding_callbacks = [];
    let render_callbacks = [];
    const flush_callbacks = [];
    const resolved_promise = /* @__PURE__ */ Promise.resolve();
    let update_scheduled = false;
    function schedule_update() {
        if (!update_scheduled) {
            update_scheduled = true;
            resolved_promise.then(flush);
        }
    }
    function add_render_callback(fn) {
        render_callbacks.push(fn);
    }
    // flush() calls callbacks in this order:
    // 1. All beforeUpdate callbacks, in order: parents before children
    // 2. All bind:this callbacks, in reverse order: children before parents.
    // 3. All afterUpdate callbacks, in order: parents before children. EXCEPT
    //    for afterUpdates called during the initial onMount, which are called in
    //    reverse order: children before parents.
    // Since callbacks might update component values, which could trigger another
    // call to flush(), the following steps guard against this:
    // 1. During beforeUpdate, any updated components will be added to the
    //    dirty_components array and will cause a reentrant call to flush(). Because
    //    the flush index is kept outside the function, the reentrant call will pick
    //    up where the earlier call left off and go through all dirty components. The
    //    current_component value is saved and restored so that the reentrant call will
    //    not interfere with the "parent" flush() call.
    // 2. bind:this callbacks cannot trigger new flush() calls.
    // 3. During afterUpdate, any updated components will NOT have their afterUpdate
    //    callback called a second time; the seen_callbacks set, outside the flush()
    //    function, guarantees this behavior.
    const seen_callbacks = new Set();
    let flushidx = 0; // Do *not* move this inside the flush() function
    function flush() {
        // Do not reenter flush while dirty components are updated, as this can
        // result in an infinite loop. Instead, let the inner flush handle it.
        // Reentrancy is ok afterwards for bindings etc.
        if (flushidx !== 0) {
            return;
        }
        const saved_component = current_component;
        do {
            // first, call beforeUpdate functions
            // and update components
            try {
                while (flushidx < dirty_components.length) {
                    const component = dirty_components[flushidx];
                    flushidx++;
                    set_current_component(component);
                    update(component.$$);
                }
            }
            catch (e) {
                // reset dirty state to not end up in a deadlocked state and then rethrow
                dirty_components.length = 0;
                flushidx = 0;
                throw e;
            }
            set_current_component(null);
            dirty_components.length = 0;
            flushidx = 0;
            while (binding_callbacks.length)
                binding_callbacks.pop()();
            // then, once components are updated, call
            // afterUpdate functions. This may cause
            // subsequent updates...
            for (let i = 0; i < render_callbacks.length; i += 1) {
                const callback = render_callbacks[i];
                if (!seen_callbacks.has(callback)) {
                    // ...so guard against infinite loops
                    seen_callbacks.add(callback);
                    callback();
                }
            }
            render_callbacks.length = 0;
        } while (dirty_components.length);
        while (flush_callbacks.length) {
            flush_callbacks.pop()();
        }
        update_scheduled = false;
        seen_callbacks.clear();
        set_current_component(saved_component);
    }
    function update($$) {
        if ($$.fragment !== null) {
            $$.update();
            run_all($$.before_update);
            const dirty = $$.dirty;
            $$.dirty = [-1];
            $$.fragment && $$.fragment.p($$.ctx, dirty);
            $$.after_update.forEach(add_render_callback);
        }
    }
    /**
     * Useful for example to execute remaining `afterUpdate` callbacks before executing `destroy`.
     */
    function flush_render_callbacks(fns) {
        const filtered = [];
        const targets = [];
        render_callbacks.forEach((c) => fns.indexOf(c) === -1 ? filtered.push(c) : targets.push(c));
        targets.forEach((c) => c());
        render_callbacks = filtered;
    }
    const outroing = new Set();
    function transition_in(block, local) {
        if (block && block.i) {
            outroing.delete(block);
            block.i(local);
        }
    }

    const globals = (typeof window !== 'undefined'
        ? window
        : typeof globalThis !== 'undefined'
            ? globalThis
            : global);

    const _boolean_attributes = [
        'allowfullscreen',
        'allowpaymentrequest',
        'async',
        'autofocus',
        'autoplay',
        'checked',
        'controls',
        'default',
        'defer',
        'disabled',
        'formnovalidate',
        'hidden',
        'inert',
        'ismap',
        'loop',
        'multiple',
        'muted',
        'nomodule',
        'novalidate',
        'open',
        'playsinline',
        'readonly',
        'required',
        'reversed',
        'selected'
    ];
    /**
     * List of HTML boolean attributes (e.g. `<input disabled>`).
     * Source: https://html.spec.whatwg.org/multipage/indices.html
     */
    new Set([..._boolean_attributes]);
    function mount_component(component, target, anchor, customElement) {
        const { fragment, after_update } = component.$$;
        fragment && fragment.m(target, anchor);
        if (!customElement) {
            // onMount happens before the initial afterUpdate
            add_render_callback(() => {
                const new_on_destroy = component.$$.on_mount.map(run).filter(is_function);
                // if the component was destroyed immediately
                // it will update the `$$.on_destroy` reference to `null`.
                // the destructured on_destroy may still reference to the old array
                if (component.$$.on_destroy) {
                    component.$$.on_destroy.push(...new_on_destroy);
                }
                else {
                    // Edge case - component was destroyed immediately,
                    // most likely as a result of a binding initialising
                    run_all(new_on_destroy);
                }
                component.$$.on_mount = [];
            });
        }
        after_update.forEach(add_render_callback);
    }
    function destroy_component(component, detaching) {
        const $$ = component.$$;
        if ($$.fragment !== null) {
            flush_render_callbacks($$.after_update);
            run_all($$.on_destroy);
            $$.fragment && $$.fragment.d(detaching);
            // TODO null out other refs, including component.$$ (but need to
            // preserve final state?)
            $$.on_destroy = $$.fragment = null;
            $$.ctx = [];
        }
    }
    function make_dirty(component, i) {
        if (component.$$.dirty[0] === -1) {
            dirty_components.push(component);
            schedule_update();
            component.$$.dirty.fill(0);
        }
        component.$$.dirty[(i / 31) | 0] |= (1 << (i % 31));
    }
    function init(component, options, instance, create_fragment, not_equal, props, append_styles, dirty = [-1]) {
        const parent_component = current_component;
        set_current_component(component);
        const $$ = component.$$ = {
            fragment: null,
            ctx: [],
            // state
            props,
            update: noop,
            not_equal,
            bound: blank_object(),
            // lifecycle
            on_mount: [],
            on_destroy: [],
            on_disconnect: [],
            before_update: [],
            after_update: [],
            context: new Map(options.context || (parent_component ? parent_component.$$.context : [])),
            // everything else
            callbacks: blank_object(),
            dirty,
            skip_bound: false,
            root: options.target || parent_component.$$.root
        };
        append_styles && append_styles($$.root);
        let ready = false;
        $$.ctx = instance
            ? instance(component, options.props || {}, (i, ret, ...rest) => {
                const value = rest.length ? rest[0] : ret;
                if ($$.ctx && not_equal($$.ctx[i], $$.ctx[i] = value)) {
                    if (!$$.skip_bound && $$.bound[i])
                        $$.bound[i](value);
                    if (ready)
                        make_dirty(component, i);
                }
                return ret;
            })
            : [];
        $$.update();
        ready = true;
        run_all($$.before_update);
        // `false` as a special case of no DOM component
        $$.fragment = create_fragment ? create_fragment($$.ctx) : false;
        if (options.target) {
            if (options.hydrate) {
                const nodes = children(options.target);
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.l(nodes);
                nodes.forEach(detach);
            }
            else {
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.c();
            }
            if (options.intro)
                transition_in(component.$$.fragment);
            mount_component(component, options.target, options.anchor, options.customElement);
            flush();
        }
        set_current_component(parent_component);
    }
    /**
     * Base class for Svelte components. Used when dev=false.
     */
    class SvelteComponent {
        $destroy() {
            destroy_component(this, 1);
            this.$destroy = noop;
        }
        $on(type, callback) {
            if (!is_function(callback)) {
                return noop;
            }
            const callbacks = (this.$$.callbacks[type] || (this.$$.callbacks[type] = []));
            callbacks.push(callback);
            return () => {
                const index = callbacks.indexOf(callback);
                if (index !== -1)
                    callbacks.splice(index, 1);
            };
        }
        $set($$props) {
            if (this.$$set && !is_empty($$props)) {
                this.$$.skip_bound = true;
                this.$$set($$props);
                this.$$.skip_bound = false;
            }
        }
    }

    function dispatch_dev(type, detail) {
        document.dispatchEvent(custom_event(type, Object.assign({ version: '3.58.0' }, detail), { bubbles: true }));
    }
    function append_dev(target, node) {
        dispatch_dev('SvelteDOMInsert', { target, node });
        append(target, node);
    }
    function insert_dev(target, node, anchor) {
        dispatch_dev('SvelteDOMInsert', { target, node, anchor });
        insert(target, node, anchor);
    }
    function detach_dev(node) {
        dispatch_dev('SvelteDOMRemove', { node });
        detach(node);
    }
    function listen_dev(node, event, handler, options, has_prevent_default, has_stop_propagation, has_stop_immediate_propagation) {
        const modifiers = options === true ? ['capture'] : options ? Array.from(Object.keys(options)) : [];
        if (has_prevent_default)
            modifiers.push('preventDefault');
        if (has_stop_propagation)
            modifiers.push('stopPropagation');
        if (has_stop_immediate_propagation)
            modifiers.push('stopImmediatePropagation');
        dispatch_dev('SvelteDOMAddEventListener', { node, event, handler, modifiers });
        const dispose = listen(node, event, handler, options);
        return () => {
            dispatch_dev('SvelteDOMRemoveEventListener', { node, event, handler, modifiers });
            dispose();
        };
    }
    function attr_dev(node, attribute, value) {
        attr(node, attribute, value);
        if (value == null)
            dispatch_dev('SvelteDOMRemoveAttribute', { node, attribute });
        else
            dispatch_dev('SvelteDOMSetAttribute', { node, attribute, value });
    }
    function prop_dev(node, property, value) {
        node[property] = value;
        dispatch_dev('SvelteDOMSetProperty', { node, property, value });
    }
    function set_data_dev(text, data) {
        data = '' + data;
        if (text.data === data)
            return;
        dispatch_dev('SvelteDOMSetData', { node: text, data });
        text.data = data;
    }
    function validate_each_argument(arg) {
        if (typeof arg !== 'string' && !(arg && typeof arg === 'object' && 'length' in arg)) {
            let msg = '{#each} only iterates over array-like objects.';
            if (typeof Symbol === 'function' && arg && Symbol.iterator in arg) {
                msg += ' You can use a spread to convert this iterable into an array.';
            }
            throw new Error(msg);
        }
    }
    function validate_slots(name, slot, keys) {
        for (const slot_key of Object.keys(slot)) {
            if (!~keys.indexOf(slot_key)) {
                console.warn(`<${name}> received an unexpected slot "${slot_key}".`);
            }
        }
    }
    /**
     * Base class for Svelte components with some minor dev-enhancements. Used when dev=true.
     */
    class SvelteComponentDev extends SvelteComponent {
        constructor(options) {
            if (!options || (!options.target && !options.$$inline)) {
                throw new Error("'target' is a required option");
            }
            super();
        }
        $destroy() {
            super.$destroy();
            this.$destroy = () => {
                console.warn('Component was already destroyed'); // eslint-disable-line no-console
            };
        }
        $capture_state() { }
        $inject_state() { }
    }

    /* src\App.svelte generated by Svelte v3.58.0 */

    const { console: console_1 } = globals;
    const file = "src\\App.svelte";

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[7] = list[i];
    	return child_ctx;
    }

    // (52:2) {#each apimessage as guildinfo}
    function create_each_block(ctx) {
    	let div11;
    	let div10;
    	let div0;
    	let h3;
    	let t0;
    	let t1_value = /*guildinfo*/ ctx[7].name + "";
    	let t1;
    	let t2;
    	let h4;
    	let t3;
    	let t4_value = /*guildinfo*/ ctx[7].server.name + "";
    	let t4;
    	let t5;
    	let p0;
    	let t6_value = /*guildinfo*/ ctx[7].server.desc + "";
    	let t6;
    	let t7;
    	let div9;
    	let div2;
    	let div1;
    	let p1;
    	let t9;
    	let label0;
    	let input0;
    	let input0_checked_value;
    	let t10;
    	let span0;
    	let t11;
    	let div4;
    	let div3;
    	let p2;
    	let t13;
    	let label1;
    	let input1;
    	let input1_checked_value;
    	let t14;
    	let span1;
    	let t15;
    	let div6;
    	let div5;
    	let p3;
    	let t17;
    	let label2;
    	let input2;
    	let input2_checked_value;
    	let t18;
    	let span2;
    	let t19;
    	let div8;
    	let div7;
    	let p4;
    	let t21;
    	let label3;
    	let input3;
    	let input3_checked_value;
    	let t22;
    	let span3;
    	let t23;
    	let mounted;
    	let dispose;

    	function click_handler() {
    		return /*click_handler*/ ctx[2](/*guildinfo*/ ctx[7]);
    	}

    	function click_handler_1() {
    		return /*click_handler_1*/ ctx[3](/*guildinfo*/ ctx[7]);
    	}

    	function click_handler_2() {
    		return /*click_handler_2*/ ctx[4](/*guildinfo*/ ctx[7]);
    	}

    	function click_handler_3() {
    		return /*click_handler_3*/ ctx[5](/*guildinfo*/ ctx[7]);
    	}

    	const block = {
    		c: function create() {
    			div11 = element("div");
    			div10 = element("div");
    			div0 = element("div");
    			h3 = element("h3");
    			t0 = text("Guild: ");
    			t1 = text(t1_value);
    			t2 = space();
    			h4 = element("h4");
    			t3 = text("Server: ");
    			t4 = text(t4_value);
    			t5 = space();
    			p0 = element("p");
    			t6 = text(t6_value);
    			t7 = space();
    			div9 = element("div");
    			div2 = element("div");
    			div1 = element("div");
    			p1 = element("p");
    			p1.textContent = "Show events location";
    			t9 = space();
    			label0 = element("label");
    			input0 = element("input");
    			t10 = space();
    			span0 = element("span");
    			t11 = space();
    			div4 = element("div");
    			div3 = element("div");
    			p2 = element("p");
    			p2.textContent = "Show distance to events";
    			t13 = space();
    			label1 = element("label");
    			input1 = element("input");
    			t14 = space();
    			span1 = element("span");
    			t15 = space();
    			div6 = element("div");
    			div5 = element("div");
    			p3 = element("p");
    			p3.textContent = "Show vending machines location";
    			t17 = space();
    			label2 = element("label");
    			input2 = element("input");
    			t18 = space();
    			span2 = element("span");
    			t19 = space();
    			div8 = element("div");
    			div7 = element("div");
    			p4 = element("p");
    			p4.textContent = "Show distance to vending machines";
    			t21 = space();
    			label3 = element("label");
    			input3 = element("input");
    			t22 = space();
    			span3 = element("span");
    			t23 = space();
    			attr_dev(h3, "class", "svelte-1ocd0an");
    			add_location(h3, file, 55, 12, 1409);
    			attr_dev(h4, "class", "svelte-1ocd0an");
    			add_location(h4, file, 56, 12, 1454);
    			attr_dev(p0, "class", "svelte-1ocd0an");
    			add_location(p0, file, 57, 6, 1501);
    			attr_dev(div0, "class", "flip-card-front svelte-1ocd0an");
    			add_location(div0, file, 54, 5, 1367);
    			attr_dev(p1, "class", "svelte-1ocd0an");
    			add_location(p1, file, 62, 16, 1661);
    			attr_dev(div1, "class", "text-box svelte-1ocd0an");
    			add_location(div1, file, 61, 14, 1622);
    			attr_dev(input0, "type", "checkbox");
    			input0.checked = input0_checked_value = /*guildinfo*/ ctx[7].notification_settings.event_show_location;
    			attr_dev(input0, "class", "svelte-1ocd0an");
    			add_location(input0, file, 65, 16, 1763);
    			attr_dev(span0, "class", "slider round svelte-1ocd0an");
    			add_location(span0, file, 66, 16, 1910);
    			attr_dev(label0, "class", "switch svelte-1ocd0an");
    			add_location(label0, file, 64, 14, 1724);
    			attr_dev(div2, "class", "row svelte-1ocd0an");
    			add_location(div2, file, 60, 12, 1590);
    			attr_dev(p2, "class", "svelte-1ocd0an");
    			add_location(p2, file, 71, 16, 2070);
    			attr_dev(div3, "class", "text-box svelte-1ocd0an");
    			add_location(div3, file, 70, 14, 2031);
    			attr_dev(input1, "type", "checkbox");
    			input1.checked = input1_checked_value = /*guildinfo*/ ctx[7].notification_settings.event_show_distance;
    			attr_dev(input1, "class", "svelte-1ocd0an");
    			add_location(input1, file, 74, 16, 2175);
    			attr_dev(span1, "class", "slider round svelte-1ocd0an");
    			add_location(span1, file, 75, 16, 2322);
    			attr_dev(label1, "class", "switch svelte-1ocd0an");
    			add_location(label1, file, 73, 14, 2136);
    			attr_dev(div4, "class", "row svelte-1ocd0an");
    			add_location(div4, file, 69, 12, 1999);
    			attr_dev(p3, "class", "svelte-1ocd0an");
    			add_location(p3, file, 80, 16, 2482);
    			attr_dev(div5, "class", "text-box svelte-1ocd0an");
    			add_location(div5, file, 79, 14, 2443);
    			attr_dev(input2, "type", "checkbox");
    			input2.checked = input2_checked_value = /*guildinfo*/ ctx[7].notification_settings.vend_show_location;
    			attr_dev(input2, "class", "svelte-1ocd0an");
    			add_location(input2, file, 83, 16, 2594);
    			attr_dev(span2, "class", "slider round svelte-1ocd0an");
    			add_location(span2, file, 84, 16, 2740);
    			attr_dev(label2, "class", "switch svelte-1ocd0an");
    			add_location(label2, file, 82, 14, 2555);
    			attr_dev(div6, "class", "row svelte-1ocd0an");
    			add_location(div6, file, 78, 12, 2411);
    			attr_dev(p4, "class", "svelte-1ocd0an");
    			add_location(p4, file, 89, 16, 2900);
    			attr_dev(div7, "class", "text-box svelte-1ocd0an");
    			add_location(div7, file, 88, 14, 2861);
    			attr_dev(input3, "type", "checkbox");
    			input3.checked = input3_checked_value = /*guildinfo*/ ctx[7].notification_settings.vend_show_distance;
    			attr_dev(input3, "class", "svelte-1ocd0an");
    			add_location(input3, file, 92, 16, 3015);
    			attr_dev(span3, "class", "slider round svelte-1ocd0an");
    			add_location(span3, file, 93, 16, 3161);
    			attr_dev(label3, "class", "switch svelte-1ocd0an");
    			add_location(label3, file, 91, 14, 2976);
    			attr_dev(div8, "class", "row svelte-1ocd0an");
    			add_location(div8, file, 87, 12, 2829);
    			attr_dev(div9, "class", "flip-card-back svelte-1ocd0an");
    			add_location(div9, file, 59, 5, 1549);
    			attr_dev(div10, "class", "flip-card-inner svelte-1ocd0an");
    			add_location(div10, file, 53, 4, 1332);
    			attr_dev(div11, "class", "flip-card svelte-1ocd0an");
    			add_location(div11, file, 52, 3, 1304);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div11, anchor);
    			append_dev(div11, div10);
    			append_dev(div10, div0);
    			append_dev(div0, h3);
    			append_dev(h3, t0);
    			append_dev(h3, t1);
    			append_dev(div0, t2);
    			append_dev(div0, h4);
    			append_dev(h4, t3);
    			append_dev(h4, t4);
    			append_dev(div0, t5);
    			append_dev(div0, p0);
    			append_dev(p0, t6);
    			append_dev(div10, t7);
    			append_dev(div10, div9);
    			append_dev(div9, div2);
    			append_dev(div2, div1);
    			append_dev(div1, p1);
    			append_dev(div2, t9);
    			append_dev(div2, label0);
    			append_dev(label0, input0);
    			append_dev(label0, t10);
    			append_dev(label0, span0);
    			append_dev(div9, t11);
    			append_dev(div9, div4);
    			append_dev(div4, div3);
    			append_dev(div3, p2);
    			append_dev(div4, t13);
    			append_dev(div4, label1);
    			append_dev(label1, input1);
    			append_dev(label1, t14);
    			append_dev(label1, span1);
    			append_dev(div9, t15);
    			append_dev(div9, div6);
    			append_dev(div6, div5);
    			append_dev(div5, p3);
    			append_dev(div6, t17);
    			append_dev(div6, label2);
    			append_dev(label2, input2);
    			append_dev(label2, t18);
    			append_dev(label2, span2);
    			append_dev(div9, t19);
    			append_dev(div9, div8);
    			append_dev(div8, div7);
    			append_dev(div7, p4);
    			append_dev(div8, t21);
    			append_dev(div8, label3);
    			append_dev(label3, input3);
    			append_dev(label3, t22);
    			append_dev(label3, span3);
    			append_dev(div11, t23);

    			if (!mounted) {
    				dispose = [
    					listen_dev(input0, "click", click_handler, false, false, false, false),
    					listen_dev(input1, "click", click_handler_1, false, false, false, false),
    					listen_dev(input2, "click", click_handler_2, false, false, false, false),
    					listen_dev(input3, "click", click_handler_3, false, false, false, false)
    				];

    				mounted = true;
    			}
    		},
    		p: function update(new_ctx, dirty) {
    			ctx = new_ctx;
    			if (dirty & /*apimessage*/ 1 && t1_value !== (t1_value = /*guildinfo*/ ctx[7].name + "")) set_data_dev(t1, t1_value);
    			if (dirty & /*apimessage*/ 1 && t4_value !== (t4_value = /*guildinfo*/ ctx[7].server.name + "")) set_data_dev(t4, t4_value);
    			if (dirty & /*apimessage*/ 1 && t6_value !== (t6_value = /*guildinfo*/ ctx[7].server.desc + "")) set_data_dev(t6, t6_value);

    			if (dirty & /*apimessage*/ 1 && input0_checked_value !== (input0_checked_value = /*guildinfo*/ ctx[7].notification_settings.event_show_location)) {
    				prop_dev(input0, "checked", input0_checked_value);
    			}

    			if (dirty & /*apimessage*/ 1 && input1_checked_value !== (input1_checked_value = /*guildinfo*/ ctx[7].notification_settings.event_show_distance)) {
    				prop_dev(input1, "checked", input1_checked_value);
    			}

    			if (dirty & /*apimessage*/ 1 && input2_checked_value !== (input2_checked_value = /*guildinfo*/ ctx[7].notification_settings.vend_show_location)) {
    				prop_dev(input2, "checked", input2_checked_value);
    			}

    			if (dirty & /*apimessage*/ 1 && input3_checked_value !== (input3_checked_value = /*guildinfo*/ ctx[7].notification_settings.vend_show_distance)) {
    				prop_dev(input3, "checked", input3_checked_value);
    			}
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div11);
    			mounted = false;
    			run_all(dispose);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block.name,
    		type: "each",
    		source: "(52:2) {#each apimessage as guildinfo}",
    		ctx
    	});

    	return block;
    }

    function create_fragment(ctx) {
    	let header;
    	let h1;
    	let t1;
    	let main;
    	let div;
    	let each_value = /*apimessage*/ ctx[0];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block(get_each_context(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			header = element("header");
    			h1 = element("h1");
    			h1.textContent = "DIRUPL";
    			t1 = space();
    			main = element("main");
    			div = element("div");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(h1, "class", "svelte-1ocd0an");
    			add_location(h1, file, 46, 2, 1199);
    			attr_dev(header, "class", "svelte-1ocd0an");
    			add_location(header, file, 45, 0, 1188);
    			attr_dev(div, "class", "cards-container svelte-1ocd0an");
    			add_location(div, file, 50, 2, 1235);
    			attr_dev(main, "class", "svelte-1ocd0an");
    			add_location(main, file, 49, 0, 1226);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, header, anchor);
    			append_dev(header, h1);
    			insert_dev(target, t1, anchor);
    			insert_dev(target, main, anchor);
    			append_dev(main, div);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				if (each_blocks[i]) {
    					each_blocks[i].m(div, null);
    				}
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*apimessage, doPost*/ 3) {
    				each_value = /*apimessage*/ ctx[0];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(div, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(header);
    			if (detaching) detach_dev(t1);
    			if (detaching) detach_dev(main);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function getCookie(name) {
    	let cookieValue = null;

    	if (document.cookie && document.cookie !== '') {
    		const cookies = document.cookie.split(';');

    		for (let i = 0; i < cookies.length; i++) {
    			const cookie = cookies[i].trim();

    			// Does this cookie string begin with the name we want?
    			if (cookie.substring(0, name.length + 1) === name + '=') {
    				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
    				break;
    			}
    		}
    	}

    	return cookieValue;
    }

    function instance($$self, $$props, $$invalidate) {
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots('App', slots, []);
    	const csrftoken = getCookie('csrftoken');
    	let apimessage = [];

    	onMount(async () => {
    		let resp = await fetch("/api/checkservers").then(res => res.json());
    		console.log(resp);
    		$$invalidate(0, apimessage = resp);
    	});

    	async function doPost(id, type) {
    		await fetch("/api/checkservers", {
    			method: 'POST',
    			body: JSON.stringify({ 'guildinfo': id, 'setting_type': type }),
    			headers: {
    				"Content-Type": "application/json",
    				'X-CSRFToken': csrftoken
    			},
    			mode: 'same-origin'
    		});
    	}

    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== '$$' && key !== 'slot') console_1.warn(`<App> was created with unknown prop '${key}'`);
    	});

    	const click_handler = guildinfo => doPost(guildinfo.id, 'esl');
    	const click_handler_1 = guildinfo => doPost(guildinfo.id, 'esd');
    	const click_handler_2 = guildinfo => doPost(guildinfo.id, 'vsl');
    	const click_handler_3 = guildinfo => doPost(guildinfo.id, 'vsd');

    	$$self.$capture_state = () => ({
    		onMount,
    		getCookie,
    		csrftoken,
    		apimessage,
    		doPost
    	});

    	$$self.$inject_state = $$props => {
    		if ('apimessage' in $$props) $$invalidate(0, apimessage = $$props.apimessage);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	return [
    		apimessage,
    		doPost,
    		click_handler,
    		click_handler_1,
    		click_handler_2,
    		click_handler_3
    	];
    }

    class App extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance, create_fragment, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "App",
    			options,
    			id: create_fragment.name
    		});
    	}
    }

    const app = new App({
    	target: document.body,
    	props: {
    		name: 'world'
    	}
    });

    return app;

})();
//# sourceMappingURL=bundle.js.map
